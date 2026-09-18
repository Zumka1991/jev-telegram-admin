from __future__ import annotations

import datetime as dt
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatPermissions

from app import texts
from app.db import repository
from app.db.models import (
    ACTION_BAN,
    ACTION_DELETE,
    ACTION_MUTE,
    ACTION_WARN,
    ChatSettings,
)
from app.i18n import t
from app.services.moderation import Decision

log = logging.getLogger(__name__)


async def _notify(
    bot: Bot,
    *,
    chat_id: int,
    message_id: int,
    settings: ChatSettings,
    text: str,
) -> None:
    if not settings.notify:
        return
    try:
        await bot.send_message(
            chat_id,
            text,
            reply_to_message_id=message_id,
            disable_web_page_preview=True,
        )
    except TelegramAPIError:
        try:
            await bot.send_message(chat_id, text, disable_web_page_preview=True)
        except TelegramAPIError as exc:
            log.debug("Не удалось отправить уведомление: %s", exc)


async def apply_decision(
    bot: Bot,
    *,
    chat_id: int,
    message_id: int,
    user_id: int,
    user_name: str,
    settings: ChatSettings,
    decision: Decision,
    excerpt: str = "",
) -> None:
    action = decision.action
    mention = texts.user_mention(user_id, user_name)

    # На действие «предупреждение» исходное сообщение оставляем.
    if action in (ACTION_DELETE, ACTION_MUTE, ACTION_BAN):
        try:
            await bot.delete_message(chat_id, message_id)
        except TelegramAPIError as exc:
            log.warning("Не удалось удалить сообщение %s: %s", message_id, exc)

    actual_action = action
    warnings: int | None = None

    try:
        if action == ACTION_WARN:
            warnings = await repository.add_warning(chat_id, user_id)
            if warnings >= settings.warn_limit:
                await bot.ban_chat_member(chat_id, user_id)
                actual_action = ACTION_BAN
            else:
                await repository.log_violation(
                    chat_id=chat_id,
                    user_id=user_id,
                    message_id=message_id,
                    category=decision.category,
                    confidence=decision.confidence,
                    action=action,
                    excerpt=excerpt,
                )

        elif action == ACTION_MUTE:
            minutes = decision.mute_minutes or settings.mute_minutes
            until = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)
            await bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until,
            )

        elif action == ACTION_BAN:
            await bot.ban_chat_member(chat_id, user_id)
            await repository.reset_warnings(chat_id, user_id)

        elif action == ACTION_DELETE:
            await repository.bump_violation(chat_id, user_id)

    except TelegramAPIError as exc:
        log.warning("Не удалось применить действие %s: %s", action, exc)
        await _notify(
            bot,
            chat_id=chat_id,
            message_id=message_id,
            settings=settings,
            text=t(settings.language, "no_rights"),
        )
        return

    if actual_action != ACTION_WARN:
        await repository.log_violation(
            chat_id=chat_id,
            user_id=user_id,
            message_id=message_id,
            category=decision.category,
            confidence=decision.confidence,
            action=actual_action,
            excerpt=excerpt,
        )

    notice = texts.violation_notice(
        lang=settings.language,
        category=decision.category,
        action=actual_action,
        mention=mention,
        warnings=warnings,
        warn_limit=settings.warn_limit,
        mute_minutes=decision.mute_minutes or settings.mute_minutes,
        spam_type=decision.spam_type,
        heuristics=decision.heuristics,
    )
    if actual_action == ACTION_BAN and action == ACTION_WARN:
        notice += "\n" + t(
            settings.language, "warn_limit_reached", limit=settings.warn_limit
        )
    log.info(
        "Модерация: chat=%s user=%s category=%s conf=%.2f action=%s",
        chat_id,
        user_id,
        decision.category,
        decision.confidence,
        actual_action,
    )
    await _notify(
        bot,
        chat_id=chat_id,
        message_id=message_id,
        settings=settings,
        text=notice,
    )

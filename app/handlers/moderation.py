from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.types import Message

from app.config import settings as app_settings
from app.db import repository
from app.db.models import ACTION_OFF
from app.i18n import t
from app.services import fallback
from app.services.actions import apply_decision
from app.services.autodelete import auto_delete
from app.services.history import flood_tracker, recent_context
from app.services.jev import ModerationResult, jev_client
from app.services.moderation import decide, enrich_with_heuristics
from app.services.telegram_utils import display_name, is_admin

log = logging.getLogger(__name__)
router = Router(name="moderation")


async def _analyze(
    *,
    chat_id: int,
    user_id: int,
    text: str,
    context: list[dict[str, str]],
) -> ModerationResult:
    if app_settings.jev_enabled:
        result = await jev_client.moderate_safe(
            text,
            recent_context=context,
            session_id=f"chat-{chat_id}",
        )
        if not result.failed:
            return result
        log.info("Jev недоступен, перехожу на резервные правила")
    return fallback.rule_based(text)


@router.message(
    F.chat.type.in_({"group", "supergroup"}),
    F.text,
    ~F.text.startswith("/"),
)
async def handle_group_message(message: Message, bot: Bot) -> None:
    user = message.from_user
    if user is None or user.is_bot:
        return

    chat_id = message.chat.id
    log.info(
        "Получено сообщение: chat=%s user=%s text=%r",
        chat_id, user.id, (message.text or message.caption or "")[:80],
    )
    settings = await repository.get_settings(
        chat_id, message.chat.title, language=user.language_code
    )
    if not settings.enabled:
        log.info("Модерация в чате %s выключена — пропускаю", chat_id)
        return
    if settings.ignore_admins and await is_admin(bot, chat_id, user.id):
        log.info(
            "Пользователь %s — админ, а включён режим «игнорировать админов» — пропускаю",
            user.id,
        )
        return

    text = message.text or message.caption or ""
    if not text.strip():
        return

    name = display_name(user)

    # 1. Флуд — быстрая эвристика до обращения к модели.
    if settings.flood_enabled and settings.action_for("flood") != ACTION_OFF:
        if flood_tracker.hit(
            chat_id=chat_id,
            user_id=user.id,
            limit=settings.flood_messages,
            window_seconds=settings.flood_seconds,
        ):
            decision = decide(
                settings,
                ModerationResult(),
                forced_category="flood",
                forced_confidence=1.0,
            )
            if decision is not None:
                await apply_decision(
                    bot,
                    chat_id=chat_id,
                    message_id=message.message_id,
                    user_id=user.id,
                    user_name=name,
                    settings=settings,
                    decision=decision,
                    excerpt=text[:200],
                )
                recent_context.add(chat_id, name, text)
                return

    # 2. AI-анализ (Jev) + эвристики рассылок.
    context = recent_context.snapshot(chat_id)
    result = await _analyze(
        chat_id=chat_id, user_id=user.id, text=text, context=context
    )
    result = enrich_with_heuristics(
        result, chat_id=chat_id, user_id=user.id, text=text
    )

    decision = decide(settings, result)
    if decision is not None:
        await apply_decision(
            bot,
            chat_id=chat_id,
            message_id=message.message_id,
            user_id=user.id,
            user_name=name,
            settings=settings,
            decision=decision,
            excerpt=text[:200],
        )

    recent_context.add(chat_id, name, text)


@router.message(F.new_chat_members)
async def handle_new_members(message: Message, bot: Bot) -> None:
    if not any(member.id == bot.id for member in message.new_chat_members):
        return
    settings = await repository.get_settings(
        message.chat.id,
        message.chat.title,
        language=message.from_user.language_code if message.from_user else None,
    )
    lang = settings.language
    sent = await message.answer(t(lang, "start") + t(lang, "help"))
    auto_delete.schedule(
        bot, message.chat.id, sent.message_id, settings.self_delete_seconds or 0
    )

from __future__ import annotations

import logging
from dataclasses import replace

from aiogram import Bot, F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message

from app.config import settings as app_settings
from app.db import repository
from app.db.models import ACTION_DELETE, ACTION_MUTE, ACTION_OFF, ACTION_WARN
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

_USER_CONTENT_FIELDS = (
    "text",
    "animation",
    "audio",
    "contact",
    "dice",
    "document",
    "game",
    "location",
    "paid_media",
    "photo",
    "poll",
    "sticker",
    "story",
    "venue",
    "video",
    "video_note",
    "voice",
)
_KNOWN_COMMANDS = {
    "start",
    "help",
    "settings",
    "stats",
    "check",
    "warn",
    "unwarn",
    "resetwarns",
}


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


def _has_user_content(message: Message) -> bool:
    """Отсекает join/pin/topic и другие сервисные сообщения от антифлуда."""
    return any(getattr(message, field, None) is not None for field in _USER_CONTENT_FIELDS)


def _text_to_analyze(message: Message) -> str:
    text = message.text or message.caption or ""
    if not text.startswith("/"):
        return text

    # У команды проверяем аргументы: префикс '/' больше не является обходом.
    # После модерации известная команда будет передана command-router'у.
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) == 2 else ""


def _is_known_command(message: Message) -> bool:
    text = message.text or ""
    if not text.startswith("/"):
        return False
    command = text.split(maxsplit=1)[0][1:].split("@", 1)[0].lower()
    return command in _KNOWN_COMMANDS


async def _handle_group_message(
    message: Message,
    bot: Bot,
    *,
    count_flood: bool,
) -> None:
    user = message.from_user
    sender_chat = message.sender_chat
    if user is None and sender_chat is None:
        return
    if user is not None and user.id == bot.id:
        return

    # Анонимный админ публикует от имени самой группы. Каналы также могут
    # писать в discussion-группу через sender_chat.
    posted_as_chat = sender_chat is not None
    actor_id = sender_chat.id if sender_chat is not None else user.id
    actor_name = (
        sender_chat.title or sender_chat.username or str(sender_chat.id)
        if sender_chat is not None
        else display_name(user)
    )

    chat_id = message.chat.id
    log.info(
        "Получено сообщение: chat=%s user=%s text=%r",
        chat_id, actor_id, (message.text or message.caption or "")[:80],
    )
    settings = await repository.get_settings(
        chat_id,
        message.chat.title,
        language=user.language_code if user is not None else None,
    )
    if not settings.enabled:
        log.info("Модерация в чате %s выключена — пропускаю", chat_id)
        return
    is_anonymous_admin = sender_chat is not None and sender_chat.id == chat_id
    actor_is_admin = is_anonymous_admin or (
        user is not None and await is_admin(bot, chat_id, user.id)
    )
    if settings.ignore_admins and actor_is_admin:
        log.info(
            "Пользователь %s — админ, а включён режим «игнорировать админов» — пропускаю",
            actor_id,
        )
        return

    if not _has_user_content(message):
        return

    if await repository.violation_exists(chat_id, message.message_id):
        return

    text = _text_to_analyze(message)

    # 1. Флуд — быстрая эвристика до обращения к модели.
    flood_detected = (
        count_flood
        and settings.flood_enabled
        and settings.action_for("flood") != ACTION_OFF
        and flood_tracker.hit(
            chat_id=chat_id,
            user_id=actor_id,
            limit=settings.flood_messages,
            window_seconds=settings.flood_seconds,
            event_id=message.media_group_id or message.message_id,
        )
    )
    if flood_detected:
        decision = decide(
            settings,
            ModerationResult(),
            forced_category="flood",
            forced_confidence=1.0,
        )
        if decision is not None:
            bot_cannot_receive_action = (
                user is not None
                and user.is_bot
                and decision.action in {ACTION_WARN, ACTION_MUTE}
            )
            if posted_as_chat or actor_is_admin or bot_cannot_receive_action:
                decision = replace(
                    decision, action=ACTION_DELETE, mute_minutes=None
                )
            await apply_decision(
                bot,
                chat_id=chat_id,
                message_id=message.message_id,
                user_id=actor_id,
                user_name=actor_name,
                settings=settings,
                decision=decision,
                excerpt=(message.text or message.caption or "")[:200],
            )
            flood_tracker.reset(chat_id, actor_id)
            if text:
                recent_context.add(chat_id, actor_name, text)
            return

    # 2. AI-анализ (Jev) + эвристики рассылок.
    if not text:
        return
    context = recent_context.snapshot(chat_id)
    result = await _analyze(
        chat_id=chat_id, user_id=actor_id, text=text, context=context
    )
    result = enrich_with_heuristics(
        result, chat_id=chat_id, user_id=actor_id, text=text
    )

    decision = decide(settings, result)
    if decision is not None:
        # Telegram не позволяет мутить sender_chat или другого администратора.
        # Если админов не игнорируют, применимое действие для них — удаление.
        bot_cannot_receive_action = (
            user is not None
            and user.is_bot
            and decision.action in {ACTION_WARN, ACTION_MUTE}
        )
        if posted_as_chat or actor_is_admin or bot_cannot_receive_action:
            decision = replace(decision, action=ACTION_DELETE, mute_minutes=None)
        await apply_decision(
            bot,
            chat_id=chat_id,
            message_id=message.message_id,
            user_id=actor_id,
            user_name=actor_name,
            settings=settings,
            decision=decision,
            excerpt=text[:200],
        )

    recent_context.add(chat_id, actor_name, text)


@router.message(F.migrate_to_chat_id)
async def handle_chat_migration(message: Message) -> None:
    await repository.migrate_chat(
        message.chat.id,
        message.migrate_to_chat_id,
        message.chat.title,
    )
    log.info(
        "Настройки группы перенесены: %s -> %s",
        message.chat.id,
        message.migrate_to_chat_id,
    )


@router.message(F.migrate_from_chat_id)
async def handle_migrated_chat(message: Message) -> None:
    await repository.migrate_chat(
        message.migrate_from_chat_id,
        message.chat.id,
        message.chat.title,
    )


@router.message(
    F.chat.type.in_({"group", "supergroup"}),
    ~F.new_chat_members,
)
async def handle_group_message(message: Message, bot: Bot) -> None:
    await _handle_group_message(message, bot, count_flood=True)
    if _is_known_command(message):
        # Moderation-router подключён первым, чтобы аргументы команд нельзя было
        # использовать как обход. После проверки передаём саму команду дальше.
        raise SkipHandler


@router.edited_message(F.chat.type.in_({"group", "supergroup"}))
async def handle_edited_group_message(message: Message, bot: Bot) -> None:
    # Редактирование проверяется заново, но не считается новым сообщением для
    # антифлуда.
    await _handle_group_message(message, bot, count_flood=False)


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

from __future__ import annotations

import logging

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app import texts
from app.config import settings as app_settings
from app.db import repository
from app.db.models import ChatSettings
from app.i18n import default_language, normalize_language, t
from app.services import fallback
from app.services.autodelete import auto_delete
from app.services.jev import jev_client
from app.services.telegram_utils import display_name, is_admin
from app.texts import user_mention

log = logging.getLogger(__name__)
router = Router(name="commands")

GROUP_TYPES = {"group", "supergroup"}
CHECK_CATEGORIES = ("profanity", "insult", "fraud", "bullying", "trolling", "spam")


def _user_lang(message: Message) -> str:
    if message.from_user and message.from_user.language_code:
        return normalize_language(
            message.from_user.language_code, fallback=default_language()
        )
    return default_language()


async def _chat_settings(message: Message) -> ChatSettings | None:
    if message.chat.type not in GROUP_TYPES:
        return None
    return await repository.get_settings(
        message.chat.id,
        message.chat.title,
        language=message.from_user.language_code if message.from_user else None,
    )


def _lang(message: Message, settings: ChatSettings | None) -> str:
    return settings.language if settings is not None else _user_lang(message)


async def _reply(
    message: Message,
    text: str,
    settings: ChatSettings | None,
    **kwargs: object,
) -> None:
    """Отправляет ответ и, если включено, планирует его автоудаление."""
    sent = await message.answer(text, **kwargs)
    if settings is not None:
        auto_delete.schedule(
            message.bot, message.chat.id, sent.message_id, settings.self_delete_seconds
        )


async def _require_admin(message: Message, bot: Bot, lang: str) -> bool:
    if message.chat.type not in GROUP_TYPES:
        await message.answer(t(lang, "group_only"))
        return False
    if message.from_user and await is_admin(bot, message.chat.id, message.from_user.id):
        return True
    await message.answer(t(lang, "admins_only"))
    return False


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    await _reply(message, t(lang, "start") + t(lang, "help"), settings)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    await _reply(message, t(lang, "help"), settings)


@router.message(Command("settings"))
async def cmd_settings(message: Message, bot: Bot) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    if not await _require_admin(message, bot, lang):
        return
    from app.handlers.settings_ui import send_settings_menu

    await send_settings_menu(bot, message.chat.id, message.chat.title)


@router.message(Command("stats"))
async def cmd_stats(message: Message, bot: Bot) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    if not await _require_admin(message, bot, lang):
        return

    chat_id = message.chat.id
    by_category = await repository.chat_stats(chat_id)
    offenders = await repository.top_offenders(chat_id)

    lines = [t(lang, "stats_title"), ""]
    if not by_category:
        lines.append(t(lang, "stats_empty"))
    else:
        total = sum(count for _, count in by_category)
        lines.append(t(lang, "stats_total", total=total))
        for category, count in by_category:
            lines.append(f"• {texts.category_label(lang, category)}: <b>{count}</b>")
    if offenders:
        lines.append("")
        lines.append(t(lang, "stats_top"))
        for user_id, count in offenders:
            lines.append(f"• {user_mention(user_id, f'ID {user_id}')}: {count}")
    await _reply(message, "\n".join(lines), settings)


@router.message(Command("warn"))
async def cmd_warn(message: Message, bot: Bot, command: CommandObject) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    if not await _require_admin(message, bot, lang):
        return
    if message.reply_to_message is None or message.reply_to_message.from_user is None:
        await _reply(message, t(lang, "reply_required", command="/warn"), settings)
        return
    target = message.reply_to_message.from_user
    if await is_admin(bot, message.chat.id, target.id):
        await _reply(message, t(lang, "cannot_warn_admin"), settings)
        return

    warn_limit = settings.warn_limit if settings else 3
    warnings = await repository.add_warning(message.chat.id, target.id)
    mention = user_mention(target.id, display_name(target))
    actual_action = "warn"
    if warnings >= warn_limit:
        try:
            await bot.ban_chat_member(message.chat.id, target.id)
        except TelegramAPIError:
            await repository.log_violation(
                chat_id=message.chat.id,
                user_id=target.id,
                message_id=message.reply_to_message.message_id,
                category="manual",
                confidence=1.0,
                action=actual_action,
                excerpt=(command.args or "")[:200],
            )
            await _reply(message, t(lang, "no_rights"), settings)
            return
        actual_action = "ban"
        await repository.reset_warnings(message.chat.id, target.id)
    await repository.log_violation(
        chat_id=message.chat.id,
        user_id=target.id,
        message_id=message.reply_to_message.message_id,
        category="manual",
        confidence=1.0,
        action=actual_action,
        excerpt=(command.args or "")[:200],
    )
    if actual_action == "ban":
        await _reply(message, t(lang, "warn_ban", mention=mention, limit=warn_limit), settings)
    else:
        await _reply(
            message,
            t(lang, "warn_given", mention=mention, count=warnings, limit=warn_limit),
            settings,
        )


@router.message(Command("unwarn"))
async def cmd_unwarn(message: Message, bot: Bot) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    if not await _require_admin(message, bot, lang):
        return
    if message.reply_to_message is None or message.reply_to_message.from_user is None:
        await _reply(message, t(lang, "reply_required", command="/unwarn"), settings)
        return
    target = message.reply_to_message.from_user
    stats = await repository.get_user_stats(message.chat.id, target.id)
    mention = user_mention(target.id, display_name(target))
    if stats.warnings <= 0:
        await _reply(message, t(lang, "no_warnings", mention=mention), settings)
        return
    await repository.reset_warnings(message.chat.id, target.id)
    await _reply(message, t(lang, "unwarn_done", mention=mention), settings)


@router.message(Command("resetwarns"))
async def cmd_reset(message: Message, bot: Bot) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    if not await _require_admin(message, bot, lang):
        return
    if message.reply_to_message is None or message.reply_to_message.from_user is None:
        await _reply(message, t(lang, "reply_required", command="/resetwarns"), settings)
        return
    target = message.reply_to_message.from_user
    await repository.reset_warnings(message.chat.id, target.id)
    mention = user_mention(target.id, display_name(target))
    await _reply(message, t(lang, "reset_done", mention=mention), settings)


@router.message(Command("check"))
async def cmd_check(message: Message, bot: Bot, command: CommandObject) -> None:
    settings = await _chat_settings(message)
    lang = _lang(message, settings)
    if not await _require_admin(message, bot, lang):
        return
    text = (command.args or "").strip()
    if not text:
        await _reply(message, t(lang, "check_usage"), settings)
        return
    if app_settings.jev_enabled:
        result = await jev_client.moderate_safe(text, session_id=f"check-{message.chat.id}")
        if result.failed:
            result = fallback.rule_based(text)
    else:
        result = fallback.rule_based(text)

    lines = [t(lang, "check_title")]
    for category in CHECK_CATEGORIES:
        probability = result.probability(category)
        filled = round(probability * 10)
        bar = "█" * filled + "░" * (10 - filled)
        lines.append(f"{texts.category_label(lang, category)}: {probability:.2f} {bar}")
    if result.severity is not None:
        lines.append(t(lang, "check_severity", value=f"{result.severity:.1f}"))
    if result.choices.get("spam_type") and result.choices["spam_type"] != "none":
        lines.append(
            t(lang, "check_spam_type", type=t(lang, f"spam_{result.choices['spam_type']}"))
        )
    punishment = result.choices.get("punishment")
    if punishment:
        extra = ""
        if punishment == "mute" and result.choices.get("mute_duration"):
            extra = f" ({result.choices['mute_duration']})"
        lines.append(
            t(
                lang,
                "check_recommendation",
                action=texts.action_label(lang, punishment),
                extra=extra,
            )
        )
    if result.heuristics:
        signals = ", ".join(texts.heuristic_labels(lang, result.heuristics))
        lines.append(t(lang, "check_evidence", list=signals))
    lines.append(t(lang, "check_model", model=result.model))
    await _reply(message, "\n".join(lines), settings)

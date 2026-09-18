from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import texts
from app.db import repository
from app.db.models import (
    ACTION_OFF,
    ACTION_ORDER,
    AI_ACTION_CATEGORIES,
    ChatSettings,
)
from app.i18n import (
    LANGUAGE_FLAGS,
    LANGUAGE_NAMES,
    LANGUAGE_ORDER,
    default_language,
    t,
)
from app.services.autodelete import auto_delete
from app.services.telegram_utils import bot_can_moderate, is_admin

router = Router(name="settings")

WARN_LIMITS = (1, 3, 5, 10)
MUTE_MINUTES = (10, 60, 1440, 10080)
THRESHOLDS = (0.40, 0.50, 0.60, 0.75)
SELF_DELETE_OPTIONS = (0, 30, 60, 300, 3600)

TOGGLE_FIELDS = ("ignore_admins", "notify", "flood_enabled")
ALL_CATEGORIES = (*AI_ACTION_CATEGORIES, "flood")


def _lang(settings: ChatSettings) -> str:
    return settings.language or default_language()


def _duration_label(lang: str, minutes: int) -> str:
    if minutes == 1440:
        return t(lang, "duration_day_1")
    if minutes == 10080:
        return t(lang, "duration_days", value=7)
    return str(minutes)


def _self_delete_label(lang: str, seconds: int) -> str:
    if seconds <= 0:
        return t(lang, "duration_off")
    if seconds < 60:
        return t(lang, "duration_seconds", value=seconds)
    if seconds < 3600:
        return t(lang, "duration_minutes", value=seconds // 60)
    return t(lang, "duration_hours", value=seconds // 3600)


def _menu_markup(settings: ChatSettings) -> InlineKeyboardMarkup:
    lang = _lang(settings)
    kb = InlineKeyboardBuilder()
    status = t(lang, "status_on" if settings.enabled else "status_off")
    kb.button(text=t(lang, "btn_moderation", status=status), callback_data="st:toggle:enabled")
    kb.button(text=t(lang, "btn_params"), callback_data="st:params")
    for category in ALL_CATEGORIES:
        action = settings.action_for(category)
        label = t(lang, f"cat_{category}")
        emoji = texts.CATEGORY_EMOJI.get(category, "•")
        mark = texts.ACTION_EMOJI.get(action, "")
        kb.button(
            text=f"{emoji} {label}: {mark} {texts.action_label(lang, action)}",
            callback_data=f"st:cat:{category}",
        )
    kb.button(text=t(lang, "btn_language"), callback_data="st:language")
    kb.button(text=t(lang, "btn_check_rights"), callback_data="st:rights")
    kb.button(text=t(lang, "btn_refresh"), callback_data="st:menu")
    kb.adjust(1, 1, *([1] * len(ALL_CATEGORIES)), 2, 1)
    return kb.as_markup()


def _menu_text(settings: ChatSettings, title: str | None) -> str:
    lang = _lang(settings)
    status = t(lang, "status_on" if settings.enabled else "status_off")
    return "\n".join(
        [
            t(lang, "settings_chat", title=title or settings.chat_id),
            t(lang, "settings_moderation", status=status),
            t(lang, "settings_threshold", value=f"{settings.threshold:.2f}"),
            t(lang, "settings_warn_limit", value=settings.warn_limit),
            t(lang, "settings_mute", value=settings.mute_minutes),
            "",
            t(lang, "settings_hint"),
        ]
    )


def _category_markup(settings: ChatSettings, category: str) -> InlineKeyboardMarkup:
    lang = _lang(settings)
    kb = InlineKeyboardBuilder()
    current = settings.action_for(category)
    for action in ACTION_ORDER:
        mark = "✅ " if current == action else ""
        kb.button(
            text=f"{mark}{texts.ACTION_EMOJI[action]} {texts.action_label(lang, action)}",
            callback_data=f"st:set:{category}:{action}",
        )
    kb.button(text=t(lang, "btn_back"), callback_data="st:menu")
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()


def _category_text(settings: ChatSettings, category: str) -> str:
    lang = _lang(settings)
    label = t(lang, f"cat_{category}")
    emoji = texts.CATEGORY_EMOJI.get(category, "•")
    if category == "flood":
        threshold = t(
            lang,
            "category_flood_threshold",
            messages=settings.flood_messages,
            seconds=settings.flood_seconds,
        )
    else:
        threshold = t(lang, "category_threshold", value=f"{settings.threshold:.2f}")
    return "\n\n".join(
        [
            t(lang, "category_title", emoji=emoji, label=label),
            threshold,
            t(lang, "category_current", action=texts.action_label(lang, settings.action_for(category))),
            t(lang, "category_hint"),
        ]
    )


def _params_markup(settings: ChatSettings) -> InlineKeyboardMarkup:
    lang = _lang(settings)
    kb = InlineKeyboardBuilder()
    for field in TOGGLE_FIELDS:
        value = getattr(settings, field)
        kb.button(
            text=f"{'✅' if value else '⬜️'} {t(lang, f'toggle_{field}')}",
            callback_data=f"st:toggle:{field}",
        )
    kb.button(text=t(lang, "params_warn_header"), callback_data="st:noop")
    for limit in WARN_LIMITS:
        kb.button(
            text=f"{'✅ ' if settings.warn_limit == limit else ''}{limit}",
            callback_data=f"st:wl:{limit}",
        )
    kb.button(text=t(lang, "params_mute_header"), callback_data="st:noop")
    for minutes in MUTE_MINUTES:
        kb.button(
            text=f"{'✅ ' if settings.mute_minutes == minutes else ''}"
            f"{_duration_label(lang, minutes)}",
            callback_data=f"st:mm:{minutes}",
        )
    kb.button(text=t(lang, "params_threshold_header"), callback_data="st:noop")
    for value in THRESHOLDS:
        kb.button(
            text=f"{'✅ ' if abs(settings.threshold - value) < 1e-6 else ''}{value:.2f}",
            callback_data=f"st:th:{value:.2f}",
        )
    kb.button(text=t(lang, "params_self_delete_header"), callback_data="st:noop")
    for seconds in SELF_DELETE_OPTIONS:
        kb.button(
            text=f"{'✅ ' if settings.self_delete_seconds == seconds else ''}"
            f"{_self_delete_label(lang, seconds)}",
            callback_data=f"st:sd:{seconds}",
        )
    kb.button(text=t(lang, "btn_back"), callback_data="st:menu")
    kb.adjust(
        len(TOGGLE_FIELDS), 1, len(WARN_LIMITS), 1, len(MUTE_MINUTES), 1,
        len(THRESHOLDS), 1, len(SELF_DELETE_OPTIONS), 1,
    )
    return kb.as_markup()


def _params_text(settings: ChatSettings) -> str:
    lang = _lang(settings)
    yes = t(lang, "params_yes")
    no = t(lang, "params_no")

    def yn(value: bool) -> str:
        return yes if value else no

    return "\n".join(
        [
            t(lang, "params_title"),
            t(lang, "params_ignore_admins", value=yn(settings.ignore_admins)),
            t(lang, "params_notify", value=yn(settings.notify)),
            t(lang, "params_flood", value=yn(settings.flood_enabled)),
            t(lang, "params_warn_limit", value=settings.warn_limit),
            t(lang, "params_mute", value=settings.mute_minutes),
            t(lang, "params_threshold", value=f"{settings.threshold:.2f}"),
            t(
                lang,
                "params_self_delete",
                value=_self_delete_label(lang, settings.self_delete_seconds),
            ),
        ]
    )


def _language_markup(settings: ChatSettings) -> InlineKeyboardMarkup:
    lang = _lang(settings)
    kb = InlineKeyboardBuilder()
    for code in LANGUAGE_ORDER:
        mark = "✅ " if settings.language == code else ""
        kb.button(
            text=f"{mark}{LANGUAGE_FLAGS[code]} {LANGUAGE_NAMES[code]}",
            callback_data=f"st:lang:{code}",
        )
    kb.button(text=t(lang, "btn_back"), callback_data="st:menu")
    kb.adjust(1, 1, 1, 1, 1, 1)
    return kb.as_markup()


def _language_text(settings: ChatSettings) -> str:
    lang = _lang(settings)
    return t(lang, "language_title") + "\n\n" + t(lang, "language_hint")


async def send_settings_menu(bot: Bot, chat_id: int, title: str | None) -> None:
    settings = await repository.get_settings(chat_id, title)
    sent = await bot.send_message(
        chat_id,
        _menu_text(settings, title),
        reply_markup=_menu_markup(settings),
        disable_web_page_preview=True,
    )
    auto_delete.schedule(
        bot, chat_id, sent.message_id, settings.self_delete_seconds or 0
    )


@router.callback_query(F.data.startswith("st:"))
async def on_settings_callback(callback: CallbackQuery, bot: Bot) -> None:
    data = callback.data or ""
    if callback.from_user is None or callback.message is None:
        await callback.answer()
        return
    chat_id = callback.message.chat.id
    if not await is_admin(bot, chat_id, callback.from_user.id):
        await callback.answer(t(default_language(), "alert_admins_only"), show_alert=True)
        return

    settings = await repository.get_settings(chat_id, callback.message.chat.title)
    lang = _lang(settings)
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else "menu"

    if action == "noop":
        await callback.answer()
        return

    if action == "toggle" and len(parts) == 3:
        field = parts[2]
        if field in ("enabled", *TOGGLE_FIELDS):
            setattr(settings, field, not getattr(settings, field))
            await repository.save_settings(settings)
        await callback.answer(t(lang, "alert_saved"))

    elif action == "wl" and len(parts) == 3:
        settings.warn_limit = int(parts[2])
        await repository.save_settings(settings)
        await callback.answer(t(lang, "alert_warn_limit", value=settings.warn_limit))

    elif action == "mm" and len(parts) == 3:
        settings.mute_minutes = int(parts[2])
        await repository.save_settings(settings)
        await callback.answer(t(lang, "alert_mute", value=settings.mute_minutes))

    elif action == "th" and len(parts) == 3:
        settings.threshold = float(parts[2])
        await repository.save_settings(settings)
        await callback.answer(t(lang, "alert_threshold", value=f"{settings.threshold:.2f}"))

    elif action == "sd" and len(parts) == 3:
        settings.self_delete_seconds = int(parts[2])
        await repository.save_settings(settings)
        await callback.answer(
            t(
                lang,
                "alert_self_delete",
                value=_self_delete_label(lang, settings.self_delete_seconds),
            )
        )

    elif action == "set" and len(parts) == 4:
        _, _, category, value = parts
        if category in ALL_CATEGORIES:
            setattr(settings, f"action_{category}", value)
            await repository.save_settings(settings)
        await callback.answer(t(lang, "alert_saved"))

    elif action == "lang" and len(parts) == 3:
        code = parts[2]
        if code in LANGUAGE_NAMES:
            settings.language = code
            await repository.save_settings(settings)
            lang = code
            await _edit(callback, _language_text(settings), _language_markup(settings))
            await callback.answer(t(lang, "alert_language", name=LANGUAGE_NAMES[code]))
            return
        await callback.answer()

    elif action == "cat" and len(parts) == 3:
        category = parts[2]
        await _edit(
            callback,
            _category_text(settings, category),
            _category_markup(settings, category),
        )
        await callback.answer()
        return

    elif action == "params":
        await _edit(callback, _params_text(settings), _params_markup(settings))
        await callback.answer()
        return

    elif action == "language":
        await _edit(callback, _language_text(settings), _language_markup(settings))
        await callback.answer()
        return

    elif action == "rights":
        if await bot_can_moderate(bot, chat_id):
            await callback.answer(t(lang, "alert_rights_ok"), show_alert=True)
        else:
            await callback.answer(t(lang, "alert_rights_missing"), show_alert=True)
        return

    await _edit(
        callback,
        _menu_text(settings, callback.message.chat.title),
        _menu_markup(settings),
    )
    await callback.answer()


async def _edit(
    callback: CallbackQuery,
    text: str,
    markup: InlineKeyboardMarkup,
) -> None:
    if callback.message is None:
        return
    try:
        await callback.message.edit_text(
            text, reply_markup=markup, disable_web_page_preview=True
        )
    except Exception:
        # Сообщение могло не измениться — это не ошибка.
        pass

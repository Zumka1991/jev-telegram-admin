from __future__ import annotations

from app.db.models import (
    ACTION_AUTO,
    ACTION_BAN,
    ACTION_DELETE,
    ACTION_MUTE,
    ACTION_OFF,
    ACTION_WARN,
)
from app.i18n import t

CATEGORY_EMOJI: dict[str, str] = {
    "profanity": "🤬",
    "insult": "🗯️",
    "fraud": "🎣",
    "bullying": "💢",
    "trolling": "😈",
    "spam": "📢",
    "flood": "🌊",
}

ACTION_EMOJI: dict[str, str] = {
    ACTION_OFF: "🚫",
    ACTION_AUTO: "🤖",
    ACTION_WARN: "⚠️",
    ACTION_DELETE: "🗑️",
    ACTION_MUTE: "🔇",
    ACTION_BAN: "⛔",
}


def user_mention(user_id: int, name: str) -> str:
    safe = name.replace("<", "").replace(">", "").replace("&", "")
    return f'<a href="tg://user?id={user_id}">{safe}</a>'


def category_label(lang: str | None, category: str) -> str:
    return t(lang, f"cat_{category}")


def action_label(lang: str | None, action: str) -> str:
    return t(lang, f"action_{action}")


def heuristic_labels(lang: str | None, keys: list[str]) -> list[str]:
    result: list[str] = []
    for key in keys:
        if ":" in key:
            base, value = key.split(":", 1)
            result.append(t(lang, base, count=value))
        else:
            result.append(t(lang, key))
    return result


def violation_notice(
    *,
    lang: str | None,
    category: str,
    action: str,
    mention: str,
    warnings: int | None = None,
    warn_limit: int | None = None,
    mute_minutes: int | None = None,
    spam_type: str | None = None,
    heuristics: list[str] | None = None,
) -> str:
    label = category_label(lang, category)

    detail = ""
    if spam_type and spam_type != "none":
        detail = " (" + t(lang, f"spam_{spam_type}") + ")"
    if heuristics:
        signals = ", ".join(heuristic_labels(lang, heuristics))
        detail += "\n<i>" + t(lang, "check_evidence", list=signals) + "</i>"

    key = {
        ACTION_WARN: "violation_warn",
        ACTION_DELETE: "violation_delete",
        ACTION_MUTE: "violation_mute",
        ACTION_BAN: "violation_ban",
    }.get(action)

    if key is None:
        return f"{mention}: <b>{label}</b>{detail}."

    return t(
        lang,
        key,
        mention=mention,
        label=label,
        detail=detail,
        warnings=warnings,
        limit=warn_limit,
        minutes=mute_minutes,
    )

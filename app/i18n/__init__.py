from __future__ import annotations

from app.config import settings as app_settings
from app.i18n.locales import ar, en, es, pt, ru

LOCALES: dict[str, dict[str, str]] = {
    "en": en.STRINGS,
    "ru": ru.STRINGS,
    "es": es.STRINGS,
    "pt": pt.STRINGS,
    "ar": ar.STRINGS,
}

# Порядок отображения в меню выбора языка.
LANGUAGE_ORDER: tuple[str, ...] = ("en", "ru", "es", "pt", "ar")

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "ru": "Русский",
    "es": "Español",
    "pt": "Português",
    "ar": "العربية",
}

LANGUAGE_FLAGS: dict[str, str] = {
    "en": "🇬🇧",
    "ru": "🇷🇺",
    "es": "🇪🇸",
    "pt": "🇧🇷",
    "ar": "🇸🇦",
}

FALLBACK_LANGUAGE = "en"


def default_language() -> str:
    return normalize_language(app_settings.default_language)


def normalize_language(code: str | None, fallback: str | None = None) -> str:
    """Приводит код языка (например, ru-RU) к поддерживаемому. Иначе — fallback."""
    default = fallback or FALLBACK_LANGUAGE
    if not code:
        return default
    base = code.strip().lower().replace("_", "-").split("-")[0]
    return base if base in LOCALES else default


def t(lang: str | None, key: str, **kwargs: object) -> str:
    """Возвращает строку перевода с подстановкой параметров."""
    table = LOCALES.get(normalize_language(lang))
    text = None
    if table is not None:
        text = table.get(key)
    if text is None:
        text = LOCALES[FALLBACK_LANGUAGE].get(key)
    if text is None:
        text = key
    if not kwargs:
        return text
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError):
        return text

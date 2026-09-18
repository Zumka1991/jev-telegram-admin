from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.db.database import dispose_db, init_db
from app.handlers import commands, moderation, settings_ui
from app.i18n import LANGUAGE_ORDER, default_language, t
from app.services.jev import jev_client

log = logging.getLogger("jev")

COMMAND_DEFS = (
    ("settings", "cmd_settings"),
    ("stats", "cmd_stats"),
    ("check", "cmd_check"),
    ("warn", "cmd_warn"),
    ("unwarn", "cmd_unwarn"),
    ("resetwarns", "cmd_resetwarns"),
    ("help", "cmd_help"),
)


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)


def _commands_for(lang: str) -> list[BotCommand]:
    return [BotCommand(command=name, description=t(lang, key)) for name, key in COMMAND_DEFS]


async def set_commands(bot: Bot) -> None:
    default = default_language()
    await bot.set_my_commands(_commands_for(default))
    for lang in LANGUAGE_ORDER:
        if lang == default:
            continue
        try:
            await bot.set_my_commands(_commands_for(lang), language_code=lang)
        except Exception as exc:  # noqa: BLE001
            log.warning("Не удалось задать команды для языка %s: %s", lang, exc)


async def main() -> None:
    setup_logging()
    if not settings.jev_enabled:
        log.warning(
            "OPENROUTER_API_KEY не задан — бот работает в резервном режиме "
            "на простых правилах. Задайте ключ для AI-модерации Jev."
        )

    await init_db()
    await jev_client.start()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(commands.router)
    dp.include_router(settings_ui.router)
    dp.include_router(moderation.router)

    await set_commands(bot)
    log.info("Jev Telegram Guard запущен. Модель: %s", settings.jev_model)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await jev_client.close()
        await dispose_db()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Остановлено")

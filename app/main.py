from __future__ import annotations

import asyncio
import datetime as dt
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, Update

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


def _update_date(update: Update) -> dt.datetime | None:
    """Дата сообщения/события апдейта, если её можно определить."""
    message = update.message or update.edited_message or update.channel_post
    if message is None and update.callback_query is not None:
        message = update.callback_query.message
    return getattr(message, "date", None)


async def process_backlog(bot: Bot, dp: Dispatcher) -> None:
    """Обрабатывает сообщения, пришедшие пока бот был выключен.

    Telegram хранит неподтверждённые апдейты до 24 часов, поэтому при старте
    забираем их и прогоняем через диспетчер (с ограничением по возрасту и числу).
    Прочитать произвольную историю чата Bot API не позволяет.
    """
    if not settings.backlog_enabled or settings.backlog_limit <= 0:
        return

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(
        hours=settings.backlog_max_age_hours
    )
    allowed = dp.resolve_used_update_types()
    offset: int | None = None
    processed = 0
    skipped = 0

    while processed < settings.backlog_limit:
        batch = await bot.get_updates(
            offset=offset,
            limit=min(100, settings.backlog_limit - processed),
            timeout=0,
            allowed_updates=allowed,
        )
        if not batch:
            break
        for update in batch:
            offset = update.update_id + 1
            date = _update_date(update)
            if date is not None and date < cutoff:
                skipped += 1
                continue
            try:
                await dp.feed_update(bot, update)
                processed += 1
            except Exception as exc:  # noqa: BLE001
                log.warning("Ошибка обработки пропущенного апдейта: %s", exc)
            if processed >= settings.backlog_limit:
                break

    # Подтверждаем последний обработанный пакет. Без запроса со следующим
    # offset Telegram может снова отдать его при запуске long polling.
    if offset is not None:
        await bot.get_updates(
            offset=offset,
            limit=1,
            timeout=0,
            allowed_updates=allowed,
        )

    if processed or skipped:
        log.info(
            "Догон пропущенных сообщений: обработано %s, пропущено по возрасту %s",
            processed,
            skipped,
        )


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
    dp.include_router(moderation.router)
    dp.include_router(commands.router)
    dp.include_router(settings_ui.router)

    # Гарантируем long polling и что апдейты за время простоя не пропадут.
    await bot.delete_webhook(drop_pending_updates=False)
    await set_commands(bot)
    await process_backlog(bot, dp)

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

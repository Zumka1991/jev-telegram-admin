from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

log = logging.getLogger(__name__)


class AutoDelete:
    """Планирует удаление сообщений бота через заданный интервал.

    Задачи живут в памяти процесса: после перезапуска бота ранее запланированные
    сообщения останутся (это осознанный компромисс ради простоты).
    """

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[None]] = set()

    def schedule(
        self,
        bot: Bot,
        chat_id: int,
        message_id: int,
        delay_seconds: int,
        *,
        group_only: bool = True,
    ) -> None:
        if delay_seconds <= 0:
            return
        # В личке автоудаление обычно не нужно; message_id положительный и id > 0.
        if group_only and chat_id >= 0:
            return
        task = asyncio.create_task(
            self._delete_later(bot, chat_id, message_id, delay_seconds)
        )
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _delete_later(
        self, bot: Bot, chat_id: int, message_id: int, delay_seconds: int
    ) -> None:
        try:
            await asyncio.sleep(delay_seconds)
            await bot.delete_message(chat_id, message_id)
            log.info(
                "Автоудаление: chat=%s message=%s через %ss",
                chat_id,
                message_id,
                delay_seconds,
            )
        except asyncio.CancelledError:
            raise
        except TelegramAPIError as exc:
            log.debug("Автоудаление не удалось (%s): %s", message_id, exc)


auto_delete = AutoDelete()

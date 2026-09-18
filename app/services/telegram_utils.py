from __future__ import annotations

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner

ADMIN_STATUSES = ("creator", "administrator")


async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except TelegramAPIError:
        return False
    return member.status in ADMIN_STATUSES


async def bot_can_moderate(bot: Bot, chat_id: int) -> bool:
    try:
        me = await bot.get_chat_member(chat_id, bot.id)
    except TelegramAPIError:
        return False
    if isinstance(me, (ChatMemberOwner, ChatMemberAdministrator)):
        if me.status == "creator":
            return True
        if isinstance(me, ChatMemberAdministrator):
            return bool(me.can_delete_messages and me.can_restrict_members)
    return me.status == "creator"


def display_name(user) -> str:
    if user is None:
        return "участник"
    name = user.full_name or user.username or str(user.id)
    return name.strip()[:64]

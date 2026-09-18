from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from sqlalchemy import delete, func, select, update

from app.config import settings
from app.db.database import session_scope
from app.db.models import ChatSettings, UserStats, Violation, utcnow
from app.i18n import default_language, normalize_language


async def get_settings(
    chat_id: int,
    title: str | None = None,
    language: str | None = None,
) -> ChatSettings:
    async with session_scope() as session:
        obj = await session.get(ChatSettings, chat_id)
        if obj is None:
            obj = ChatSettings(
                chat_id=chat_id,
                title=title,
                language=(
                    normalize_language(language, fallback=default_language())
                    if language
                    else default_language()
                ),
                threshold=settings.default_threshold,
                warn_limit=settings.default_warn_limit,
                mute_minutes=settings.default_mute_minutes,
                flood_messages=settings.default_flood_messages,
                flood_seconds=settings.default_flood_seconds,
                self_delete_seconds=settings.default_self_delete_seconds,
            )
            session.add(obj)
            await session.flush()
        elif title and obj.title != title:
            obj.title = title
        await session.refresh(obj)
        session.expunge(obj)
        return obj


async def save_settings(obj: ChatSettings) -> None:
    async with session_scope() as session:
        await session.merge(obj)


async def migrate_chat(old_chat_id: int, new_chat_id: int, title: str | None) -> None:
    """Переносит настройки и историю при апгрейде группы в супергруппу."""
    if old_chat_id == new_chat_id:
        return
    async with session_scope() as session:
        old_settings = await session.get(ChatSettings, old_chat_id)
        new_settings = await session.get(ChatSettings, new_chat_id)
        if old_settings is not None and new_settings is None:
            old_settings.chat_id = new_chat_id
            if title:
                old_settings.title = title
        elif old_settings is not None:
            # Если новый чат уже успел создать настройки, считаем их более
            # свежими и убираем только устаревшую запись старого id.
            await session.execute(
                delete(ChatSettings).where(ChatSettings.chat_id == old_chat_id)
            )

        old_stats = (
            await session.scalars(
                select(UserStats).where(UserStats.chat_id == old_chat_id)
            )
        ).all()
        for old_state in old_stats:
            new_state = await session.scalar(
                select(UserStats)
                .where(
                    UserStats.chat_id == new_chat_id,
                    UserStats.user_id == old_state.user_id,
                )
                .limit(1)
            )
            if new_state is None:
                old_state.chat_id = new_chat_id
                continue
            new_state.warnings = max(
                new_state.warnings or 0, old_state.warnings or 0
            )
            new_state.violations = (
                (new_state.violations or 0) + (old_state.violations or 0)
            )
            dates = [
                value
                for value in (new_state.last_violation_at, old_state.last_violation_at)
                if value is not None
            ]
            new_state.last_violation_at = max(dates) if dates else None
            await session.delete(old_state)
        await session.execute(
            update(Violation)
            .where(Violation.chat_id == old_chat_id)
            .values(chat_id=new_chat_id)
        )


@dataclass(slots=True)
class UserState:
    warnings: int
    violations: int


async def get_user_stats(chat_id: int, user_id: int) -> UserState:
    async with session_scope() as session:
        stmt = select(UserStats).where(
            UserStats.chat_id == chat_id, UserStats.user_id == user_id
        )
        obj = (await session.execute(stmt)).scalar_one_or_none()
        if obj is None:
            obj = UserStats(chat_id=chat_id, user_id=user_id, warnings=0, violations=0)
            session.add(obj)
            await session.flush()
        return UserState(warnings=obj.warnings or 0, violations=obj.violations or 0)


async def add_warning(chat_id: int, user_id: int) -> int:
    """Добавляет предупреждение и возвращает новое количество."""
    async with session_scope() as session:
        obj = await session.scalar(
            select(UserStats).where(
                UserStats.chat_id == chat_id, UserStats.user_id == user_id
            )
        )
        if obj is None:
            obj = UserStats(chat_id=chat_id, user_id=user_id, warnings=0, violations=0)
            session.add(obj)
        obj.warnings += 1
        obj.violations += 1
        obj.last_violation_at = utcnow()
        await session.flush()
        return obj.warnings


async def reset_warnings(chat_id: int, user_id: int) -> None:
    async with session_scope() as session:
        obj = await session.scalar(
            select(UserStats).where(
                UserStats.chat_id == chat_id, UserStats.user_id == user_id
            )
        )
        if obj is not None:
            obj.warnings = 0


async def bump_violation(chat_id: int, user_id: int) -> None:
    async with session_scope() as session:
        obj = await session.scalar(
            select(UserStats).where(
                UserStats.chat_id == chat_id, UserStats.user_id == user_id
            )
        )
        if obj is None:
            obj = UserStats(chat_id=chat_id, user_id=user_id, warnings=0, violations=0)
            session.add(obj)
        obj.violations += 1
        obj.last_violation_at = utcnow()


async def log_violation(
    *,
    chat_id: int,
    user_id: int,
    message_id: int | None,
    category: str,
    confidence: float,
    action: str,
    excerpt: str,
) -> None:
    async with session_scope() as session:
        session.add(
            Violation(
                chat_id=chat_id,
                user_id=user_id,
                message_id=message_id,
                category=category,
                confidence=confidence,
                action=action,
                excerpt=excerpt[:500],
            )
        )


async def violation_exists(chat_id: int, message_id: int) -> bool:
    """Возвращает True, если это сообщение уже привело к наказанию.

    Telegram может повторно доставить апдейт после перезапуска, а изменённое
    сообщение приходит отдельным апдейтом. Эта проверка не даёт повторно
    предупредить/ограничить участника за одно и то же сообщение.
    """
    async with session_scope() as session:
        stmt = (
            select(Violation.id)
            .where(
                Violation.chat_id == chat_id,
                Violation.message_id == message_id,
            )
            .limit(1)
        )
        return (await session.scalar(stmt)) is not None


async def chat_stats(chat_id: int, days: int = 7) -> list[tuple[str, int]]:
    since = utcnow() - dt.timedelta(days=days)
    async with session_scope() as session:
        stmt = (
            select(Violation.category, func.count(Violation.id))
            .where(Violation.chat_id == chat_id, Violation.created_at >= since)
            .group_by(Violation.category)
            .order_by(func.count(Violation.id).desc())
        )
        rows = (await session.execute(stmt)).all()
        return [(row[0], int(row[1])) for row in rows]


async def top_offenders(chat_id: int, days: int = 7, limit: int = 5) -> list[tuple[int, int]]:
    since = utcnow() - dt.timedelta(days=days)
    async with session_scope() as session:
        stmt = (
            select(Violation.user_id, func.count(Violation.id))
            .where(Violation.chat_id == chat_id, Violation.created_at >= since)
            .group_by(Violation.user_id)
            .order_by(func.count(Violation.id).desc())
            .limit(limit)
        )
        rows = (await session.execute(stmt)).all()
        return [(int(row[0]), int(row[1])) for row in rows]

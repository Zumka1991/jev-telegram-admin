from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from sqlalchemy import func, select

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

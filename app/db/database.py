from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.db.models import Base

log = logging.getLogger(__name__)


def _ensure_sqlite_dir(url: str) -> None:
    prefix = "sqlite+aiosqlite:///"
    if not url.startswith(prefix):
        return
    path = url[len(prefix):]
    if path in ("", ":memory:"):
        return
    directory = os.path.dirname(os.path.abspath(path))
    if directory:
        os.makedirs(directory, exist_ok=True)


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    _ensure_sqlite_dir(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if engine.dialect.name == "sqlite":
            await _migrate_sqlite(conn)
    log.info("База данных готова")


# Простые аддитивные миграции для SQLite: добавляем отсутствующие столбцы.
_SQLITE_MIGRATIONS: dict[str, dict[str, str]] = {
    "chat_settings": {
        "action_spam": "VARCHAR(16) DEFAULT 'delete'",
        "language": "VARCHAR(8) DEFAULT 'en'",
    },
}


async def _migrate_sqlite(conn) -> None:
    for table, columns in _SQLITE_MIGRATIONS.items():
        rows = (await conn.exec_driver_sql(f"PRAGMA table_info({table})")).fetchall()
        existing = {row[1] for row in rows}
        for name, ddl in columns.items():
            if name not in existing:
                await conn.exec_driver_sql(
                    f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"
                )
                log.info("Миграция: %s.%s добавлен", table, name)


async def dispose_db() -> None:
    await engine.dispose()


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

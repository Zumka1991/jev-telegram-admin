from __future__ import annotations

import datetime as dt

from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    pass


ACTION_OFF = "off"
ACTION_AUTO = "auto"
ACTION_WARN = "warn"
ACTION_DELETE = "delete"
ACTION_MUTE = "mute"
ACTION_BAN = "ban"

# Порядок вариантов действия (для меню). Строгость: warn < delete < mute < ban.
ACTION_ORDER = [ACTION_OFF, ACTION_AUTO, ACTION_WARN, ACTION_DELETE, ACTION_MUTE, ACTION_BAN]
# Ранг конкретного действия при выборе сильнейшего нарушения в сообщении.
ACTION_RANK = {
    ACTION_OFF: 0,
    ACTION_WARN: 1,
    ACTION_DELETE: 2,
    ACTION_MUTE: 3,
    ACTION_BAN: 4,
}

CATEGORIES = ("profanity", "insult", "fraud", "bullying", "trolling", "spam", "flood")
# Категории, которые присваивает AI-движок (у флуда отдельная эвристика).
AI_ACTION_CATEGORIES = (
    "profanity",
    "insult",
    "fraud",
    "bullying",
    "trolling",
    "spam",
)


class ChatSettings(Base):
    __tablename__ = "chat_settings"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ignore_admins: Mapped[bool] = mapped_column(Boolean, default=True)
    notify: Mapped[bool] = mapped_column(Boolean, default=True)
    language: Mapped[str] = mapped_column(String(8), default="en")

    threshold: Mapped[float] = mapped_column(Float, default=0.55)
    warn_limit: Mapped[int] = mapped_column(Integer, default=3)
    mute_minutes: Mapped[int] = mapped_column(Integer, default=60)

    action_profanity: Mapped[str] = mapped_column(String(16), default=ACTION_DELETE)
    action_insult: Mapped[str] = mapped_column(String(16), default=ACTION_DELETE)
    action_fraud: Mapped[str] = mapped_column(String(16), default=ACTION_DELETE)
    action_bullying: Mapped[str] = mapped_column(String(16), default=ACTION_DELETE)
    action_trolling: Mapped[str] = mapped_column(String(16), default=ACTION_DELETE)
    action_spam: Mapped[str] = mapped_column(String(16), default=ACTION_DELETE)
    action_flood: Mapped[str] = mapped_column(String(16), default=ACTION_MUTE)

    flood_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    flood_messages: Mapped[int] = mapped_column(Integer, default=7)
    flood_seconds: Mapped[int] = mapped_column(Integer, default=10)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    def action_for(self, category: str) -> str:
        return getattr(self, f"action_{category}", ACTION_OFF) or ACTION_OFF


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)

    warnings: Mapped[int] = mapped_column(Integer, default=0)
    violations: Mapped[int] = mapped_column(Integer, default=0)
    last_violation_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Violation(Base):
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    category: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    action: Mapped[str] = mapped_column(String(16))
    excerpt: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

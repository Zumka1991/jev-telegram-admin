from __future__ import annotations

import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import DeleteMessage

os.environ.setdefault("BOT_TOKEN", "123456:test-token")

from app.db.models import ACTION_BAN, ACTION_DELETE, ACTION_WARN, ChatSettings
from app.handlers.moderation import (
    _has_user_content,
    _is_known_command,
    _text_to_analyze,
)
from app.services.actions import apply_decision
from app.services.history import FloodTracker
from app.services.moderation import Decision
from app.texts import user_mention


def message(**values: object) -> SimpleNamespace:
    defaults = {
        "text": None,
        "caption": None,
        "photo": None,
        "sticker": None,
    }
    defaults.update(values)
    return SimpleNamespace(**defaults)


def test_caption_and_unknown_command_payload_are_analyzed() -> None:
    assert _text_to_analyze(message(caption="реклама в подписи")) == "реклама в подписи"
    assert _text_to_analyze(message(text="/unknown фишинговая ссылка")) == "фишинговая ссылка"
    assert _text_to_analyze(message(text="/unknown\nфишинговая ссылка")) == "фишинговая ссылка"
    assert _text_to_analyze(message(text="/unknown")) == ""
    assert _is_known_command(message(text="/settings@MyBot payload"))
    assert not _is_known_command(message(text="/unknown payload"))


def test_media_counts_as_user_content_but_service_message_does_not() -> None:
    assert _has_user_content(message(photo=[object()]))
    assert _has_user_content(message(sticker=object()))
    assert not _has_user_content(message())


def test_album_is_one_flood_event_and_threshold_is_inclusive() -> None:
    tracker = FloodTracker()
    assert not tracker.hit(
        chat_id=-1, user_id=1, limit=3, window_seconds=10, event_id="album-1"
    )
    assert not tracker.hit(
        chat_id=-1, user_id=1, limit=3, window_seconds=10, event_id="album-1"
    )
    assert not tracker.hit(
        chat_id=-1, user_id=1, limit=3, window_seconds=10, event_id=2
    )
    assert tracker.hit(
        chat_id=-1, user_id=1, limit=3, window_seconds=10, event_id=3
    )


def test_mentions_escape_html_and_sender_chat_is_not_a_user_link() -> None:
    assert user_mention(7, "A&B <C>") == '<a href="tg://user?id=7">A&amp;B &lt;C&gt;</a>'
    assert user_mention(-100, "News <feed>") == "News &lt;feed&gt;"


def test_warning_limit_bans_and_resets_warnings() -> None:
    bot = SimpleNamespace(
        delete_message=AsyncMock(),
        ban_chat_member=AsyncMock(),
    )
    settings = ChatSettings(
        chat_id=-1,
        language="ru",
        notify=False,
        warn_limit=2,
        mute_minutes=60,
    )
    decision = Decision(category="spam", action=ACTION_WARN, confidence=0.99)

    with (
        patch("app.services.actions.repository.violation_exists", AsyncMock(return_value=False)),
        patch("app.services.actions.repository.add_warning", AsyncMock(return_value=2)),
        patch("app.services.actions.repository.reset_warnings", AsyncMock()) as reset,
        patch("app.services.actions.repository.log_violation", AsyncMock()) as log_violation,
    ):
        asyncio.run(
            apply_decision(
                bot,
                chat_id=-1,
                message_id=10,
                user_id=7,
                user_name="User",
                settings=settings,
                decision=decision,
            )
        )

    bot.ban_chat_member.assert_awaited_once_with(-1, 7)
    reset.assert_awaited_once_with(-1, 7)
    assert log_violation.await_args.kwargs["action"] == ACTION_BAN


def test_failed_delete_is_not_recorded_as_success() -> None:
    error = TelegramBadRequest(
        method=DeleteMessage(chat_id=-1, message_id=10),
        message="not enough rights",
    )
    bot = SimpleNamespace(delete_message=AsyncMock(side_effect=error))
    settings = ChatSettings(
        chat_id=-1,
        language="ru",
        notify=False,
        warn_limit=3,
        mute_minutes=60,
    )
    decision = Decision(category="spam", action=ACTION_DELETE, confidence=0.99)

    with (
        patch("app.services.actions.repository.violation_exists", AsyncMock(return_value=False)),
        patch("app.services.actions.repository.bump_violation", AsyncMock()) as bump,
        patch("app.services.actions.repository.log_violation", AsyncMock()) as log_violation,
    ):
        asyncio.run(
            apply_decision(
                bot,
                chat_id=-1,
                message_id=10,
                user_id=7,
                user_name="User",
                settings=settings,
                decision=decision,
            )
        )

    bump.assert_not_awaited()
    log_violation.assert_not_awaited()

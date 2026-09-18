from __future__ import annotations

import hashlib
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass

_FP_CLEAN = re.compile(r"[^0-9a-zа-яё\s]+", re.IGNORECASE)
_FP_WS = re.compile(r"\s+")


def fingerprint(text: str) -> str | None:
    """Отпечаток длинного сообщения для поиска одинаковых рассылок."""
    cleaned = _FP_CLEAN.sub(" ", text.lower())
    cleaned = _FP_WS.sub(" ", cleaned).strip()
    if len(cleaned) < 25:
        return None
    return hashlib.sha1(cleaned.encode("utf-8", "ignore")).hexdigest()


@dataclass(slots=True)
class RepostSignal:
    distinct_chats: int = 0
    repeat_count: int = 0


class SpamTracker:
    """Ищет одинаковые сообщения, разосланные по разным чатам одним автором."""

    def __init__(self, window_seconds: int = 24 * 3600) -> None:
        self._window = window_seconds
        self._reposts: dict[str, deque[tuple[float, int, int]]] = defaultdict(deque)

    def observe(self, *, chat_id: int, user_id: int, text: str) -> RepostSignal:
        fp = fingerprint(text)
        if fp is None:
            return RepostSignal()

        now = time.monotonic()
        cutoff = now - self._window
        events = self._reposts[fp]
        while events and events[0][0] < cutoff:
            events.popleft()
        events.append((now, chat_id, user_id))

        chats: set[int] = set()
        repeats = 0
        for _, ev_chat, ev_user in events:
            if ev_user != user_id:
                continue
            chats.add(ev_chat)
            if ev_chat == chat_id:
                repeats += 1
        return RepostSignal(distinct_chats=len(chats), repeat_count=repeats)


class RecentContext:
    """Короткая история сообщений чата для контекстного анализа (буллинг/троллинг)."""

    def __init__(self, per_chat: int = 6) -> None:
        self._per_chat = per_chat
        self._store: dict[int, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=self._per_chat)
        )

    def add(self, chat_id: int, author: str, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        self._store[chat_id].append({"author": author, "text": cleaned[:400]})

    def snapshot(self, chat_id: int) -> list[dict[str, str]]:
        return list(self._store.get(chat_id, ()))


class FloodTracker:
    """Скользящее окно сообщений на пользователя для детекции флуда."""

    def __init__(self) -> None:
        self._events: dict[tuple[int, int], deque[float]] = defaultdict(deque)

    def hit(
        self,
        *,
        chat_id: int,
        user_id: int,
        limit: int,
        window_seconds: int,
    ) -> bool:
        now = time.monotonic()
        events = self._events[(chat_id, user_id)]
        cutoff = now - window_seconds
        while events and events[0] < cutoff:
            events.popleft()
        events.append(now)
        return len(events) > limit

    def reset(self, chat_id: int, user_id: int) -> None:
        self._events.pop((chat_id, user_id), None)


recent_context = RecentContext()
flood_tracker = FloodTracker()
spam_tracker = SpamTracker()


from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.db.models import (
    ACTION_AUTO,
    ACTION_BAN,
    ACTION_DELETE,
    ACTION_MUTE,
    ACTION_OFF,
    ACTION_RANK,
    AI_ACTION_CATEGORIES,
    ChatSettings,
)
from app.services.history import spam_tracker
from app.services.jev import AI_CATEGORIES, MUTE_DURATION_MINUTES, ModerationResult

# Категории, где нарушения особенно опасны и «авто» сразу банит.
_SEVERE_CATEGORIES = {"fraud", "bullying", "spam"}

_LINKS = re.compile(r"(https?://|t\.me/|@[a-zA-Z0-9_]{4,})", re.IGNORECASE)
_JOB_WORDS = re.compile(
    r"(работ|ваканс|подработ|зарплат|доход|набор|команд|стажиров|"
    r"vacancy|hiring|salary|job|remote)",
    re.IGNORECASE,
)


def enrich_with_heuristics(
    result: ModerationResult,
    *,
    chat_id: int,
    user_id: int,
    text: str,
) -> ModerationResult:
    """Дополняет вердикт Jev эвристиками по рассылкам и ссылкам.

    Работает поверх ответа модели: повышает вероятность спама, если один и тот же
    текст рассылается по многим чатам или повторяется, и фиксирует тип спама.
    """
    if result.failed:
        return result

    signal = spam_tracker.observe(chat_id=chat_id, user_id=user_id, text=text)
    boost = 0.0

    if signal.distinct_chats >= 3:
        boost = max(boost, 0.97)
        result.heuristics.append(f"heur_repost_chats:{signal.distinct_chats}")
        result.choices.setdefault("spam_type", "job_offer")
    elif signal.distinct_chats == 2:
        boost = max(boost, 0.8)
        result.heuristics.append("heur_repost_second")
    elif signal.repeat_count >= 3:
        boost = max(boost, 0.85)
        result.heuristics.append("heur_repeat_msg")

    links = len(_LINKS.findall(text))
    if links >= 3 and _JOB_WORDS.search(text):
        boost = max(boost, 0.85)
        result.heuristics.append("heur_many_links")
        result.choices.setdefault("spam_type", "job_offer")

    if boost:
        result.probabilities["spam"] = max(result.probability("spam"), boost)

    return result


@dataclass(slots=True)
class Decision:
    category: str
    action: str
    confidence: float
    probabilities: dict[str, float] = field(default_factory=dict)
    severity: float | None = None
    spam_type: str | None = None
    heuristics: list[str] = field(default_factory=list)
    mute_minutes: int | None = None

    @property
    def is_off(self) -> bool:
        return self.action == ACTION_OFF


def _policy_action(
    category: str, confidence: float, severity: float | None
) -> tuple[str, int | None]:
    """Запасная политика, если Jev не дал рекомендацию по наказанию."""
    level = severity if severity is not None else confidence * 4.0
    if level >= 3.5 or (category in _SEVERE_CATEGORIES and confidence >= 0.85):
        return ACTION_BAN, None
    if level >= 2.0 or confidence >= 0.80:
        return ACTION_MUTE, 1440 if level >= 3.0 else 60
    return ACTION_DELETE, None


def resolve_auto(
    *,
    category: str,
    confidence: float,
    result: ModerationResult,
) -> tuple[str, int | None]:
    """Само выбирает наказание (delete/mute/ban) по тяжести нарушения.

    Приоритет — рекомендация самой модели Jev (вопрос punishment),
    иначе используется политика по severity и уверенности.
    """
    recommended = result.choices.get("punishment")
    if recommended in ("warn", ACTION_DELETE, ACTION_MUTE, ACTION_BAN):
        action = recommended
        if action == ACTION_MUTE:
            minutes = MUTE_DURATION_MINUTES.get(
                result.choices.get("mute_duration", "")
            )
            if minutes is None:
                minutes = _policy_action(category, confidence, result.severity)[1] or 60
            return action, minutes
        return action, None

    return _policy_action(category, confidence, result.severity)


def _effective_action(
    settings: ChatSettings,
    category: str,
    confidence: float,
    result: ModerationResult,
) -> tuple[str, int | None]:
    action = settings.action_for(category)
    if action == ACTION_AUTO:
        return resolve_auto(category=category, confidence=confidence, result=result)
    return action, None


def decide(
    settings: ChatSettings,
    result: ModerationResult,
    *,
    forced_category: str | None = None,
    forced_confidence: float = 1.0,
) -> Decision | None:
    """Выбирает категорию нарушения и действие по настройкам чата."""
    if result.failed and forced_category is None:
        return None

    if forced_category is not None:
        action, mute_minutes = _effective_action(
            settings, forced_category, forced_confidence, result
        )
        if action == ACTION_OFF:
            return None
        return Decision(
            category=forced_category,
            action=action,
            confidence=forced_confidence,
            probabilities=result.probabilities,
            severity=result.severity,
            spam_type=result.choices.get("spam_type"),
            heuristics=list(result.heuristics),
            mute_minutes=mute_minutes,
        )

    threshold = settings.threshold
    triggered: list[tuple[str, float, str, int | None]] = []
    for category in AI_CATEGORIES:
        if category not in AI_ACTION_CATEGORIES:
            continue
        configured = settings.action_for(category)
        if configured == ACTION_OFF:
            continue
        probability = result.probability(category)
        if probability >= threshold:
            action, mute_minutes = _effective_action(
                settings, category, probability, result
            )
            if action == ACTION_OFF:
                continue
            triggered.append((category, probability, action, mute_minutes))

    if not triggered:
        return None

    # Приоритет: сильнейшее действие; при равенстве — выше вероятность.
    category, probability, action, mute_minutes = max(
        triggered, key=lambda item: (ACTION_RANK.get(item[2], 0), item[1])
    )
    return Decision(
        category=category,
        action=action,
        confidence=probability,
        probabilities=result.probabilities,
        severity=result.severity,
        spam_type=result.choices.get("spam_type"),
        heuristics=list(result.heuristics),
        mute_minutes=mute_minutes,
    )

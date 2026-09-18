from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.config import settings

log = logging.getLogger(__name__)

AI_CATEGORIES = ("profanity", "insult", "fraud", "bullying", "trolling", "spam")

# Рекомендации Jev по наказанию -> длительность мута в минутах.
MUTE_DURATION_MINUTES: dict[str, int] = {
    "minutes_10": 10,
    "hour_1": 60,
    "day_1": 1440,
    "days_7": 10080,
    "days_30": 43200,
}

PUNISHMENT_VALUES = ("none", "warn", "delete", "mute", "ban")

# Типизированные вопросы для Jev (TypeSafe System One).
# noul -> калиброванная вероятность "да"; score -> позиция на упорядоченной шкале.
MODERATION_QUESTIONS: dict[str, dict[str, Any]] = {
    "profanity": {
        "type": "noul",
        "instructions": (
            "Содержит ли текст нецензурную брань (мат) на русском или английском языке, "
            "включая обходные написания со звёздочками, цифрами, пробелами и латиницей?"
        ),
        "criteria": {
            "true": "Есть обсценная лексика или её замаскированная форма.",
            "false": "Мата нет; допустимая разговорная или смайлики вместо ругательств.",
        },
    },
    "insult": {
        "type": "noul",
        "instructions": (
            "Содержит ли текст прямое оскорбление, унижение или грубое обзывание "
            "конкретного человека или группы лиц?"
        ),
        "criteria": {
            "true": "Есть адресное оскорбление, уничижительное сравнение или грубое обзывание.",
            "false": "Критика по делу, спор или шутка без унижения конкретных людей.",
        },
    },
    "fraud": {
        "type": "noul",
        "instructions": (
            "Содержит ли текст признаки мошенничества, скама, фишинга или обмана: "
            "просьбы перевести деньги/крипту, подозрительные ссылки, "
            "«гарантированный заработок», фиктивные розыгрыши, выманивание данных или кодов?"
        ),
        "criteria": {
            "true": "Есть схема обмана, фишинговая ссылка или выманивание денег/данных.",
            "false": "Обычное обсуждение без признаков обмана или выманивания.",
        },
    },
    "bullying": {
        "type": "noul",
        "instructions": (
            "Является ли текст травлей (буллингом): систематические насмешки, "
            "угрозы, запугивание, травля конкретного участника, в том числе "
            "с учётом приведённого контекста последних сообщений?"
        ),
        "criteria": {
            "true": "Направленное давление, угрозы или унижение жертвы, повторяющееся по контексту.",
            "false": "Разовый спор или шутка без признаков травли и запугивания.",
        },
    },
    "trolling": {
        "type": "noul",
        "instructions": (
            "Является ли текст троллингом: умышленная провокация, разжигание конфликта, "
            "высмеивание ради реакции, вбросы, не относящиеся к теме сообщения?"
        ),
        "criteria": {
            "true": "Умышленная провокация или вброс ради скандала и реакции толпы.",
            "false": "Искреннее сообщение или конструктивный спор без провокации.",
        },
    },
    "spam": {
        "type": "noul",
        "instructions": (
            "Является ли текст спамом или нежелательной массовой рекламой: "
            "предложения работы/подработки с зарплатой и призывом писать в личку, "
            "рекрутинг-разводы, инвестиционные и крипто-схемы, продвижение каналов, "
            "реферальные ссылки, «заработок из дома», набор в команды, "
            "посты с обилием ссылок или контактов не по теме беседы?"
        ),
        "criteria": {
            "true": (
                "Массовая реклама, вакансия/подработка с призывом в ЛС, "
                "инвестиционная или реферальная схема, навязчивое продвижение."
            ),
            "false": (
                "Обычное сообщение по теме, личное мнение, обсуждение или вопрос, "
                "даже если упомянута работа или ссылка по контексту."
            ),
        },
    },
    "spam_type": {
        "type": "choice",
        "instructions": (
            "Определи основной тип спама. Если спама нет — выбери none."
        ),
        "criteria": {
            "none": "Это не спам.",
            "job_offer": "Предложение работы, подработки, набора в команду, рекрутинг.",
            "crypto_scam": "Криптовалюты, инвестиции, «удвоение», заработок без усилий.",
            "phishing": "Кража данных: фишинговые ссылки, просьбы ввести пароль/код/сид-фразу.",
            "ads": "Реклама товаров, услуг, каналов, чатов, раскрутка.",
            "contact_bait": "Призыв писать в личку/переходить по ссылке без явной рекламы.",
            "other": "Иной нежелательный или массовый контент.",
        },
    },
    "severity": {
        "type": "score",
        "instructions": (
            "Насколько опасно это сообщение для сообщества? Оцени по шкале от самого "
            "низкого уровня к самому высокому."
        ),
        "criteria": [
            "Безобидно",
            "Лёгкая грубость",
            "Агрессия или конфликт",
            "Травля, угрозы или обман",
            "Криминал, угрозы жизни или крупное мошенничество",
        ],
    },
    "punishment": {
        "type": "choice",
        "instructions": (
            "Какое наказание соразмерно этому сообщению с учётом тяжести нарушения? "
            "Выбери одно: none — нарушения нет; warn — мягко предупредить; "
            "delete — удалить сообщение; mute — временно ограничить участника; "
            "ban — заблокировать (грубые, повторные или опасные нарушения: "
            "мошенничество, травля, угрозы, массовый спам)."
        ),
        "criteria": {
            "none": "Нарушения нет, реакция не нужна.",
            "warn": "Мелкое нарушение — достаточно предупреждения.",
            "delete": "Есть нарушение — сообщение нужно удалить.",
            "mute": "Серьёзное нарушение — нужен временный мут.",
            "ban": "Опасное или повторное нарушение — нужен бан.",
        },
    },
    "mute_duration": {
        "type": "choice",
        "instructions": (
            "Если уместен мут, какова разумная длительность? Если мут не нужен — none."
        ),
        "criteria": {
            "none": "Мут не нужен.",
            "minutes_10": "10 минут — мелкое нарушение.",
            "hour_1": "1 час — умеренное нарушение.",
            "day_1": "1 день — серьёзное нарушение.",
            "days_7": "7 дней — злостное нарушение.",
            "days_30": "30 дней — повторное грубое нарушение.",
        },
    },
}

# Важно: контекст (recent_context) передаётся в одном state с целевым сообщением.
# Без этого указания Jev приписывает мат/оскорбления из контекста самому сообщению
# (проверено: «Как дела» после матерных сообщений получал profanity 0.75).
# Поэтому все вопросы, кроме буллинга и троллинга, оценивают только target_message.
_TARGET_ONLY = (
    "Оценивай ТОЛЬКО текст из поля target_message. Поле recent_context — это фон "
    "переписки; не приписывай его содержание целевому сообщению. "
)
_CONTEXT_CAREFUL = (
    "Оценивай в первую очередь текст из поля target_message. Поле recent_context — "
    "только фон: оно НЕ должно повышать вероятность, если само target_message не "
    "содержит унижения, угроз, насмешек или травли конкретного участника. "
    "Повышай вероятность лишь когда target_message сам является актом травли, "
    "в том числе продолжением уже начатой травли того же человека. "
)
for _q_key in (
    "profanity",
    "insult",
    "fraud",
    "spam",
    "spam_type",
    "severity",
    "punishment",
    "mute_duration",
):
    MODERATION_QUESTIONS[_q_key]["instructions"] = (
        _TARGET_ONLY + MODERATION_QUESTIONS[_q_key]["instructions"]
    )
for _q_key in ("bullying", "trolling"):
    MODERATION_QUESTIONS[_q_key]["instructions"] = (
        _CONTEXT_CAREFUL + MODERATION_QUESTIONS[_q_key]["instructions"]
    )

# Дополнительные уточнения против ложных срабатываний на упоминаниях, а не на самих
# нарушениях: «сматерись», «мат», «ругайся» — это не брань, не оскорбление и не троллинг.
_NUANCES: dict[str, str] = {
    "profanity": (
        "Считай нецензурной бранью ТОЛЬКО фактические обсценные слова в target_message. "
        "Слова, которые лишь называют явление (мат, матерщина, ругательство, "
        "нецензурщина) или просят/разрешают выругаться (сматерись, выматерись, "
        "ругайся, напиши мат), НЕ являются бранью, если самих обсценных слов нет. "
    ),
    "insult": (
        "Считай оскорблением ТОЛЬКО фактические унижения или обзывательства в "
        "target_message, адресованные человеку или группе. Просьбы, приказы и "
        "упоминания (например «сматерись», «мат», «ругайся») оскорблением не являются. "
    ),
    "trolling": (
        "Считай троллингом ТОЛЬКО умышленную провокацию или вброс, направленные на "
        "участников и имеющие целью вызвать конфликт или бурную реакцию. Просьбы, "
        "команды и упоминания (например «сматерись», «напиши мат», «ругайся») "
        "троллингом не являются. "
    ),
}
for _q_key, _extra in _NUANCES.items():
    MODERATION_QUESTIONS[_q_key]["instructions"] = (
        _extra + MODERATION_QUESTIONS[_q_key]["instructions"]
    )



class JevError(RuntimeError):
    pass


@dataclass(slots=True)
class ModerationResult:
    probabilities: dict[str, float] = field(default_factory=dict)
    choices: dict[str, str] = field(default_factory=dict)
    severity: float | None = None
    model: str | None = None
    raw: dict[str, Any] | None = None
    failed: bool = False
    heuristics: list[str] = field(default_factory=list)

    def probability(self, category: str) -> float:
        return float(self.probabilities.get(category, 0.0))


class JevClient:
    """Клиент OpenRouter Decisions API для модели TypeSafe Jev."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        if settings.openrouter_http_referer:
            headers["HTTP-Referer"] = settings.openrouter_http_referer
        if settings.openrouter_title:
            headers["X-OpenRouter-Title"] = settings.openrouter_title
        self._client = httpx.AsyncClient(
            timeout=settings.jev_timeout_seconds,
            headers=headers,
        )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _endpoints(self) -> list[str]:
        primary = settings.jev_endpoint.rstrip("/")
        candidates = [primary]
        # Страховка от различий в версии API: /api/alpha/... и /api/v1/api/alpha/...
        if "/api/v1/" not in primary and primary.startswith("https://openrouter.ai/api/"):
            candidates.append(primary.replace("/api/", "/api/v1/api/", 1))
        return candidates

    async def moderate(
        self,
        text: str,
        *,
        recent_context: list[dict[str, str]] | None = None,
        session_id: str | None = None,
    ) -> ModerationResult:
        if not settings.jev_enabled:
            raise JevError("OPENROUTER_API_KEY не задан")
        if self._client is None:
            await self.start()

        state: dict[str, Any] = {"target_message": text}
        if recent_context:
            state["recent_context"] = recent_context

        payload: dict[str, Any] = {
            "model": settings.jev_model,
            "state": state,
            "questions": MODERATION_QUESTIONS,
            "provider": {"allow_fallbacks": True},
        }
        if session_id:
            payload["session_id"] = session_id

        assert self._client is not None
        last_error: Exception | None = None
        for url in self._endpoints():
            try:
                response = await self._client.post(url, json=payload)
                if response.status_code == 404:
                    last_error = JevError(f"404 на {url}")
                    continue
                response.raise_for_status()
                return self._parse(response.json())
            except httpx.HTTPStatusError as exc:
                body = exc.response.text[:300]
                last_error = JevError(
                    f"Jev HTTP {exc.response.status_code}: {body}"
                )
            except httpx.HTTPError as exc:  # network/timeout
                last_error = JevError(f"Сеть Jev: {exc}")
                break

        log.warning("Jev недоступен: %s", last_error)
        raise last_error or JevError("Неизвестная ошибка Jev")

    @staticmethod
    def _parse(data: dict[str, Any]) -> ModerationResult:
        answers = data.get("answers") or {}
        result = ModerationResult(model=data.get("model"), raw=data)

        for category in AI_CATEGORIES:
            answer = answers.get(category)
            if not isinstance(answer, dict):
                continue
            if answer.get("type") == "noul" and answer.get("noul") is not None:
                try:
                    result.probabilities[category] = max(
                        0.0, min(1.0, float(answer["noul"]))
                    )
                except (TypeError, ValueError):
                    continue

        severity_answer = answers.get("severity")
        if isinstance(severity_answer, dict) and severity_answer.get("score") is not None:
            try:
                result.severity = float(severity_answer["score"])
            except (TypeError, ValueError):
                result.severity = None

        spam_type = answers.get("spam_type")
        if isinstance(spam_type, dict) and spam_type.get("choice"):
            result.choices["spam_type"] = str(spam_type["choice"])

        punishment = answers.get("punishment")
        if isinstance(punishment, dict) and punishment.get("choice"):
            result.choices["punishment"] = str(punishment["choice"])

        mute_duration = answers.get("mute_duration")
        if isinstance(mute_duration, dict) and mute_duration.get("choice"):
            result.choices["mute_duration"] = str(mute_duration["choice"])

        return result

    async def moderate_safe(self, text: str, **kwargs: Any) -> ModerationResult:
        try:
            return await self.moderate(text, **kwargs)
        except JevError as exc:
            log.debug("Jev moderate_safe failed: %s", exc)
            return ModerationResult(failed=True)


jev_client = JevClient()

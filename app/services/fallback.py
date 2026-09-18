from __future__ import annotations

import re

from app.services.jev import ModerationResult

# Резервная эвристика на случай, если ключ OpenRouter не задан или Jev недоступен.
# Основной движок — Jev; это лишь «аварийный» режим с грубыми правилами.

_LEET = str.maketrans({"@": "a", "0": "o", "1": "i", "3": "e", "$": "s", "4": "a", "5": "s"})


def _normalize(text: str) -> str:
    lowered = text.lower().translate(_LEET)
    return re.sub(r"[\s\.\-\_\*\|]+", "", lowered)


_PROFANITY = re.compile(
    r"(бля|блят|блядь|хуй|хуя|хуе|хер|пизд|ебат|ебал|ебан|еба|ёба|ебуч|"
    r"сука|сучк|мудак|мудил|долбо[её]б|залуп|манда|шлюх|ублюд|гандон|говн|"
    r"fuck|fck|shit|bitch|cunt|asshole|dickhead)",
    re.IGNORECASE,
)

_INSULT = re.compile(
    r"(ты\s+(лох|дурак|идиот|дебил|тупой|тупая|ничтожество|мразь|тварь|чмо)|"
    r"(идиот|дебил|кретин|придурок|урод|мразь|тварь|чмо|ничтожество)\b|"
    r"idiot|moron|retard|loser|scum)",
    re.IGNORECASE,
)

_FRAUD = re.compile(
    r"(переведи\s+(деньги|средства)|перевод\s+на\s+карт|"
    r"гарантированн\w*\s+(заработ|доход|профит)|крипт\w*\s+удвоен|"
    r"выиграл\w*\s+(приз|деньг)|забери\s+приз|"
    r"(t\.me|bit\.ly|tinyurl|goo\.gl)/\S+|"
    r"отправь\s+(код|смс)|скажи\s+код\s+из\s+смс|"
    r"\b(seed[- ]?phrase|сид[- ]?фраз|приватн\w+ ключ)\b|"
    r"free\s+crypto|double\s+your)",
    re.IGNORECASE,
)

_THREATS = re.compile(
    r"(я\s+тебя\s+(найду|прибью|убью|закопаю)|"
    r"убью|прибью|зарежу|сожгу|"
    r"kill\s+you|i\s+will\s+find\s+you)",
    re.IGNORECASE,
)

_SPAM_JOB = re.compile(
    r"(требуются?\s+(сотрудник|люди|работник|менеджер)|"
    r"набор\s+в\s+(команду|штат)|"
    r"подработк\w*|работа\s+(онлайн|из\s+дома|удал[её]нно)|"
    r"зарплат\w*\s+(от|до)\s*\d|доход\s+(от|до)\s*\d|"
    r"оплата\s+(ежедневно|каждый\s+день)|"
    r"пиши\s+(мне\s+)?в\s+(лс|личк)|напиши\s+в\s+(лс|личк)|"
    r"(свободн\w+\s+график).{0,40}(зарплат|доход|оплат))",
    re.IGNORECASE,
)

_SPAM_CRYPTO = re.compile(
    r"(инвестиц\w+|пассивн\w+\s+доход|x2|x5|удво\w+\s+(депозит|вклад)|"
    r"бинарн\w+\s+опцион|трейд\w*\s+сигнал|"
    r"(giveaway|airdrop).{0,30}(connect\s+wallet|подключи\s+кошел))",
    re.IGNORECASE,
)

_LINK = re.compile(r"(https?://|t\.me/|@[a-zA-Z0-9_]{4,})", re.IGNORECASE)


def rule_based(text: str) -> ModerationResult:
    normalized = _normalize(text)
    probs: dict[str, float] = {}
    choices: dict[str, str] = {}

    if _PROFANITY.search(normalized) or _PROFANITY.search(text.lower()):
        probs["profanity"] = 0.9
    if _INSULT.search(text):
        probs["insult"] = 0.85
    if _FRAUD.search(text):
        probs["fraud"] = 0.9
        choices["spam_type"] = "phishing"
    if _THREATS.search(text):
        probs["bullying"] = 0.85
        probs["insult"] = max(probs.get("insult", 0.0), 0.7)
    if _SPAM_JOB.search(text):
        probs["spam"] = 0.9
        choices["spam_type"] = "job_offer"
    elif _SPAM_CRYPTO.search(text):
        probs["spam"] = 0.9
        choices["spam_type"] = "crypto_scam"

    severity = None
    if probs:
        severity = 4.0 if "fraud" in probs or "bullying" in probs else 2.0

    return ModerationResult(
        probabilities=probs,
        choices=choices,
        severity=severity,
        model="rule-based-fallback",
        raw=None,
        heuristics=["heur_rules"],
    )

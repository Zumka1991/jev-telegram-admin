"""Русские строки."""

STRINGS: dict[str, str] = {
    # General
    "start": (
        "Привет! Я <b>Jev</b> — AI-модератор.\n"
        "Добавьте меня в группу, выдайте права «Удалять сообщения» и "
        "«Ограничивать участников», и я буду следить за порядком.\n\n"
    ),
    "help": (
        "<b>Jev — AI-модератор групп</b>\n\n"
        "Я читаю сообщения и с помощью модели <b>Jev</b> (TypeSafe System One) "
        "определяю мат, оскорбления, мошенничество, буллинг, троллинг и спам, "
        "затем удаляю сообщение, выдаю мут или бан — как настроят админы.\n\n"
        "<b>Команды</b>\n"
        "/settings — настройки для этого чата (кнопки)\n"
        "/stats — статистика нарушений за 7 дней\n"
        "/warn — выдать предупреждение (ответом)\n"
        "/unwarn — снять предупреждения (ответом)\n"
        "/resetwarns — сбросить предупреждения (ответом)\n"
        "/check — проверить текст без действий\n"
        "/help — эта справка\n\n"
        "Добавьте меня в группу и выдайте права: удалять сообщения и ограничивать участников."
    ),
    "no_rights": (
        "⚠️ У меня нет нужных прав. Выдайте боту права: "
        "<i>удалять сообщения</i> и <i>ограничивать участников</i>."
    ),
    "group_only": "Эта команда работает в группе. Добавьте меня в группу и выдайте права.",
    "admins_only": "⛔ Команда доступна только администраторам чата.",
    "reply_required": "Ответьте командой {command} на сообщение участника.",
    "cannot_warn_admin": "Нельзя предупреждать администратора.",
    # Warnings
    "warn_given": "⚠️ {mention}, предупреждение {count}/{limit}.",
    "warn_ban": "⛔ {mention} забанен: лимит предупреждений ({limit}) исчерпан.",
    "no_warnings": "У {mention} нет предупреждений.",
    "unwarn_done": "✅ С {mention} сняты все предупреждения.",
    "reset_done": "✅ Предупреждения {mention} сброшены.",
    # Check
    "check_usage": "Использование: <code>/check текст для проверки</code>",
    "check_title": "<b>🔎 Проверка текста</b>",
    "check_severity": "Опасность: {value}/4",
    "check_spam_type": "Тип спама: {type}",
    "check_recommendation": "Рекомендация Jev: <b>{action}</b>{extra}",
    "check_evidence": "Признаки: {list}",
    "check_model": "<i>Модель: {model}</i>",
    # Stats
    "stats_title": "<b>📊 Статистика модерации за 7 дней</b>",
    "stats_empty": "Нарушений не зафиксировано.",
    "stats_total": "Всего нарушений: <b>{total}</b>",
    "stats_top": "<b>Топ нарушителей</b>",
    # Violations
    "violation_warn": "⚠️ {mention}, предупреждение {warnings}/{limit}: <b>{label}</b>{detail}.",
    "violation_delete": "🗑️ {mention}, сообщение удалено: <b>{label}</b>{detail}.",
    "violation_mute": "🔇 {mention}, выдан мут на <b>{minutes} мин</b>: <b>{label}</b>{detail}.",
    "violation_ban": "⛔ {mention} забанен: <b>{label}</b>{detail}.",
    "warn_limit_reached": "Лимит предупреждений ({limit}) исчерпан.",
    # Settings menu
    "settings_chat": "<b>Чат:</b> {title}",
    "settings_moderation": "<b>Модерация:</b> {status}",
    "settings_threshold": "<b>Порог:</b> {value}",
    "settings_warn_limit": "<b>Предупреждений до бана:</b> {value}",
    "settings_mute": "<b>Длительность мута:</b> {value} мин",
    "settings_hint": "<i>Нажмите на категорию, чтобы выбрать действие.</i>",
    "status_on": "включена",
    "status_off": "выключена",
    "btn_moderation": "Модерация: {status}",
    "btn_params": "⚙️ Параметры",
    "btn_check_rights": "🩺 Проверить права бота",
    "btn_refresh": "🔄 Обновить",
    "btn_back": "⬅️ Назад",
    "btn_language": "🌐 Язык",
    # Category screen
    "category_title": "{emoji} <b>{label}</b>",
    "category_threshold": "<b>Порог уверенности:</b> {value}",
    "category_flood_threshold": "<b>Порог флуда:</b> {messages} сообщений / {seconds} с",
    "category_current": "<b>Текущее действие:</b> {action}",
    "category_hint": (
        "<i>off — не реагировать, auto — бот сам решает (удалить/мут/бан) по "
        "опасности, warn — предупредить, delete — удалить, mute — мут, ban — бан.</i>"
    ),
    # Parameters screen
    "params_title": "<b>⚙️ Параметры</b>",
    "params_ignore_admins": "• Игнорировать админов: {value}",
    "params_notify": "• Уведомления: {value}",
    "params_flood": "• Детекция флуда: {value}",
    "params_warn_limit": "• Предупреждений до бана: {value}",
    "params_mute": "• Длительность мута: {value} мин",
    "params_threshold": "• Порог уверенности модели: {value}",
    "params_yes": "да",
    "params_no": "нет",
    "params_warn_header": "— Предупреждений до бана —",
    "params_mute_header": "— Длительность мута (мин) —",
    "params_threshold_header": "— Порог уверенности —",
    "toggle_ignore_admins": "Игнорировать админов",
    "toggle_notify": "Показывать уведомления",
    "toggle_flood": "Детекция флуда",
    "duration_day_1": "1 день",
    "duration_days": "{value} дней",
    # Language screen
    "language_title": "🌐 <b>Язык интерфейса</b>",
    "language_hint": "<i>Выберите язык бота для этого чата.</i>",
    # Alerts
    "alert_admins_only": "Только администраторы могут менять настройки.",
    "alert_saved": "Сохранено",
    "alert_warn_limit": "Порог предупреждений: {value}",
    "alert_mute": "Мут: {value} мин",
    "alert_threshold": "Порог: {value}",
    "alert_rights_ok": "Права в порядке ✅",
    "alert_rights_missing": "Не хватает прав: «Удалять сообщения» и «Ограничивать участников».",
    "alert_language": "Язык: {name}",
    # Categories
    "cat_profanity": "Нецензурная брань",
    "cat_insult": "Оскорбления",
    "cat_fraud": "Мошенничество",
    "cat_bullying": "Буллинг",
    "cat_trolling": "Троллинг",
    "cat_spam": "Спам",
    "cat_flood": "Флуд",
    # Actions
    "action_off": "выключено",
    "action_auto": "авто",
    "action_warn": "предупреждение",
    "action_delete": "удалять",
    "action_mute": "мут",
    "action_ban": "бан",
    # Spam types
    "spam_job_offer": "предложение работы",
    "spam_crypto_scam": "крипто-развод",
    "spam_phishing": "фишинг/кража данных",
    "spam_ads": "реклама/раскрутка",
    "spam_contact_bait": "призыв писать в личку",
    "spam_other": "прочее",
    # Heuristics
    "heur_repost_chats": "рассылка по {count} чатам",
    "heur_repost_second": "одинаковый текст во втором чате",
    "heur_repeat_msg": "повтор одного сообщения",
    "heur_many_links": "много ссылок в предложении",
    "heur_rules": "правила",
    # Command menu
    "cmd_settings": "Настройки модерации",
    "cmd_stats": "Статистика нарушений",
    "cmd_check": "Проверить текст",
    "cmd_warn": "Предупредить (ответом)",
    "cmd_unwarn": "Снять предупреждения (ответом)",
    "cmd_resetwarns": "Сбросить предупреждения (ответом)",
    "cmd_help": "Справка",
}

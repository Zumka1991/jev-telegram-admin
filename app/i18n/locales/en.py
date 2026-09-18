"""English strings (source of truth for all locales)."""

STRINGS: dict[str, str] = {
    # General
    "start": (
        "Hi! I'm <b>Jev</b>, an AI moderator.\n"
        "Add me to a group and grant the rights <i>Delete messages</i> and "
        "<i>Restrict members</i>, and I'll keep order.\n\n"
    ),
    "help": (
        "<b>Jev — AI group moderator</b>\n\n"
        "I read messages and use the <b>Jev</b> model (TypeSafe System One) to "
        "detect profanity, insults, fraud, bullying, trolling and spam, then "
        "delete the message, mute or ban — as configured by admins.\n\n"
        "<b>Commands</b>\n"
        "/settings — settings for this chat (buttons)\n"
        "/stats — violation stats for 7 days\n"
        "/warn — warn a member (reply)\n"
        "/unwarn — remove warnings (reply)\n"
        "/resetwarns — reset warnings (reply)\n"
        "/check — test a text without actions\n"
        "/help — this help\n\n"
        "Add me to a group and grant rights: delete messages and restrict members."
    ),
    "no_rights": (
        "⚠️ I don't have the required rights. Please grant me: "
        "<i>delete messages</i> and <i>restrict members</i>."
    ),
    "group_only": "This command works in a group. Add me to a group and grant the rights.",
    "admins_only": "⛔ This command is available to chat administrators only.",
    "reply_required": "Reply with {command} to a member's message.",
    "cannot_warn_admin": "You cannot warn an administrator.",
    # Warnings
    "warn_given": "⚠️ {mention}, warning {count}/{limit}.",
    "warn_ban": "⛔ {mention} was banned: warning limit ({limit}) reached.",
    "no_warnings": "{mention} has no warnings.",
    "unwarn_done": "✅ All warnings removed from {mention}.",
    "reset_done": "✅ Warnings reset for {mention}.",
    # Check
    "check_usage": "Usage: <code>/check text to analyze</code>",
    "check_title": "<b>🔎 Text check</b>",
    "check_severity": "Severity: {value}/4",
    "check_spam_type": "Spam type: {type}",
    "check_recommendation": "Jev recommendation: <b>{action}</b>{extra}",
    "check_evidence": "Signals: {list}",
    "check_model": "<i>Model: {model}</i>",
    # Stats
    "stats_title": "<b>📊 Moderation stats for 7 days</b>",
    "stats_empty": "No violations recorded.",
    "stats_total": "Total violations: <b>{total}</b>",
    "stats_top": "<b>Top offenders</b>",
    # Violations
    "violation_warn": "⚠️ {mention}, warning {warnings}/{limit}: <b>{label}</b>{detail}.",
    "violation_delete": "🗑️ {mention}, message deleted: <b>{label}</b>{detail}.",
    "violation_mute": "🔇 {mention} was muted for <b>{minutes} min</b>: <b>{label}</b>{detail}.",
    "violation_ban": "⛔ {mention} was banned: <b>{label}</b>{detail}.",
    "warn_limit_reached": "Warning limit ({limit}) reached.",
    # Settings menu
    "settings_chat": "<b>Chat:</b> {title}",
    "settings_moderation": "<b>Moderation:</b> {status}",
    "settings_threshold": "<b>Threshold:</b> {value}",
    "settings_warn_limit": "<b>Warnings before ban:</b> {value}",
    "settings_mute": "<b>Mute duration:</b> {value} min",
    "settings_hint": "<i>Tap a category to choose an action.</i>",
    "status_on": "on",
    "status_off": "off",
    "btn_moderation": "Moderation: {status}",
    "btn_params": "⚙️ Parameters",
    "btn_check_rights": "🩺 Check bot rights",
    "btn_refresh": "🔄 Refresh",
    "btn_back": "⬅️ Back",
    "btn_language": "🌐 Language",
    # Category screen
    "category_title": "{emoji} <b>{label}</b>",
    "category_threshold": "<b>Confidence threshold:</b> {value}",
    "category_flood_threshold": "<b>Flood threshold:</b> {messages} messages / {seconds} s",
    "category_current": "<b>Current action:</b> {action}",
    "category_hint": (
        "<i>off — ignore, auto — the bot decides (delete/mute/ban) by severity, "
        "warn — warn, delete — delete, mute — mute, ban — ban.</i>"
    ),
    # Parameters screen
    "params_title": "<b>⚙️ Parameters</b>",
    "params_ignore_admins": "• Ignore admins: {value}",
    "params_notify": "• Notifications: {value}",
    "params_flood": "• Flood detection: {value}",
    "params_warn_limit": "• Warnings before ban: {value}",
    "params_mute": "• Mute duration: {value} min",
    "params_threshold": "• Model confidence threshold: {value}",
    "params_yes": "yes",
    "params_no": "no",
    "params_warn_header": "— Warnings before ban —",
    "params_mute_header": "— Mute duration (min) —",
    "params_threshold_header": "— Confidence threshold —",
    "toggle_ignore_admins": "Ignore admins",
    "toggle_notify": "Notifications",
    "toggle_flood": "Flood detection",
    "duration_day_1": "1 day",
    "duration_days": "{value} days",
    # Language screen
    "language_title": "🌐 <b>Interface language</b>",
    "language_hint": "<i>Choose the bot's language for this chat.</i>",
    # Alerts
    "alert_admins_only": "Only administrators can change settings.",
    "alert_saved": "Saved",
    "alert_warn_limit": "Warning limit: {value}",
    "alert_mute": "Mute duration: {value} min",
    "alert_threshold": "Threshold: {value}",
    "alert_rights_ok": "Rights are OK ✅",
    "alert_rights_missing": "Missing rights: «Delete messages» and «Restrict members».",
    "alert_language": "Language: {name}",
    # Categories
    "cat_profanity": "Profanity",
    "cat_insult": "Insults",
    "cat_fraud": "Fraud",
    "cat_bullying": "Bullying",
    "cat_trolling": "Trolling",
    "cat_spam": "Spam",
    "cat_flood": "Flood",
    # Actions
    "action_off": "off",
    "action_auto": "auto",
    "action_warn": "warn",
    "action_delete": "delete",
    "action_mute": "mute",
    "action_ban": "ban",
    # Spam types
    "spam_job_offer": "job offer",
    "spam_crypto_scam": "crypto scam",
    "spam_phishing": "phishing/data theft",
    "spam_ads": "ads/promo",
    "spam_contact_bait": "DM bait",
    "spam_other": "other",
    # Heuristics
    "heur_repost_chats": "cross-posted to {count} chats",
    "heur_repost_second": "same text in a second chat",
    "heur_repeat_msg": "repeated message",
    "heur_many_links": "many links in a job offer",
    "heur_rules": "rules",
    # Command menu
    "cmd_settings": "Moderation settings",
    "cmd_stats": "Violation stats",
    "cmd_check": "Check a text",
    "cmd_warn": "Warn a member (reply)",
    "cmd_unwarn": "Remove warnings (reply)",
    "cmd_resetwarns": "Reset warnings (reply)",
    "cmd_help": "Help",
}

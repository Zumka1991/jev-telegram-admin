"""Cadenas en español."""

STRINGS: dict[str, str] = {
    # General
    "start": (
        "¡Hola! Soy <b>Jev</b>, un moderador con IA.\n"
        "Añádeme a un grupo y dame los permisos <i>Eliminar mensajes</i> y "
        "<i>Restringir miembros</i>, y mantendré el orden.\n\n"
    ),
    "help": (
        "<b>Jev — moderador de grupos con IA</b>\n\n"
        "Leo los mensajes y uso el modelo <b>Jev</b> (TypeSafe System One) para "
        "detectar groserías, insultos, fraude, acoso, troleo y spam; luego "
        "elimino el mensaje, silencio o baneo, según lo configuren los admins.\n\n"
        "<b>Comandos</b>\n"
        "/settings — ajustes de este chat (botones)\n"
        "/stats — estadísticas de infracciones (7 días)\n"
        "/warn — advertir a un miembro (respondiendo)\n"
        "/unwarn — quitar advertencias (respondiendo)\n"
        "/resetwarns — reiniciar advertencias (respondiendo)\n"
        "/check — analizar un texto sin actuar\n"
        "/help — esta ayuda\n\n"
        "Añádeme a un grupo y dame permisos: eliminar mensajes y restringir miembros."
    ),
    "no_rights": (
        "⚠️ No tengo los permisos necesarios. Concédeme: "
        "<i>eliminar mensajes</i> y <i>restringir miembros</i>."
    ),
    "group_only": "Este comando funciona en un grupo. Añádeme a un grupo y dame los permisos.",
    "admins_only": "⛔ Este comando solo está disponible para administradores del chat.",
    "reply_required": "Responde con {command} al mensaje de un miembro.",
    "cannot_warn_admin": "No puedes advertir a un administrador.",
    # Warnings
    "warn_given": "⚠️ {mention}, advertencia {count}/{limit}.",
    "warn_ban": "⛔ {mention} fue baneado: se alcanzó el límite de advertencias ({limit}).",
    "no_warnings": "{mention} no tiene advertencias.",
    "unwarn_done": "✅ Se quitaron todas las advertencias de {mention}.",
    "reset_done": "✅ Advertencias reiniciadas para {mention}.",
    # Check
    "check_usage": "Uso: <code>/check texto a analizar</code>",
    "check_title": "<b>🔎 Análisis de texto</b>",
    "check_severity": "Gravedad: {value}/4",
    "check_spam_type": "Tipo de spam: {type}",
    "check_recommendation": "Recomendación de Jev: <b>{action}</b>{extra}",
    "check_evidence": "Señales: {list}",
    "check_model": "<i>Modelo: {model}</i>",
    # Stats
    "stats_title": "<b>📊 Estadísticas de moderación (7 días)</b>",
    "stats_empty": "No se registraron infracciones.",
    "stats_total": "Infracciones totales: <b>{total}</b>",
    "stats_top": "<b>Infractores principales</b>",
    # Violations
    "violation_warn": "⚠️ {mention}, advertencia {warnings}/{limit}: <b>{label}</b>{detail}.",
    "violation_delete": "🗑️ {mention}, mensaje eliminado: <b>{label}</b>{detail}.",
    "violation_mute": "🔇 {mention} fue silenciado durante <b>{minutes} min</b>: <b>{label}</b>{detail}.",
    "violation_ban": "⛔ {mention} fue baneado: <b>{label}</b>{detail}.",
    "warn_limit_reached": "Se alcanzó el límite de advertencias ({limit}).",
    # Settings menu
    "settings_chat": "<b>Chat:</b> {title}",
    "settings_moderation": "<b>Moderación:</b> {status}",
    "settings_threshold": "<b>Umbral:</b> {value}",
    "settings_warn_limit": "<b>Advertencias antes del ban:</b> {value}",
    "settings_mute": "<b>Duración del silencio:</b> {value} min",
    "settings_hint": "<i>Toca una categoría para elegir una acción.</i>",
    "status_on": "activada",
    "status_off": "desactivada",
    "btn_moderation": "Moderación: {status}",
    "btn_params": "⚙️ Parámetros",
    "btn_check_rights": "🩺 Comprobar permisos del bot",
    "btn_refresh": "🔄 Actualizar",
    "btn_back": "⬅️ Atrás",
    "btn_language": "🌐 Idioma",
    # Category screen
    "category_title": "{emoji} <b>{label}</b>",
    "category_threshold": "<b>Umbral de confianza:</b> {value}",
    "category_flood_threshold": "<b>Umbral de flood:</b> {messages} mensajes / {seconds} s",
    "category_current": "<b>Acción actual:</b> {action}",
    "category_hint": (
        "<i>off — ignorar, auto — el bot decide (eliminar/silenciar/banear) según "
        "la gravedad, warn — advertir, delete — eliminar, mute — silenciar, ban — banear.</i>"
    ),
    # Parameters screen
    "params_title": "<b>⚙️ Parámetros</b>",
    "params_ignore_admins": "• Ignorar admins: {value}",
    "params_notify": "• Notificaciones: {value}",
    "params_flood": "• Detección de flood: {value}",
    "params_warn_limit": "• Advertencias antes del ban: {value}",
    "params_mute": "• Duración del silencio: {value} min",
    "params_threshold": "• Umbral de confianza del modelo: {value}",
    "params_yes": "sí",
    "params_no": "no",
    "params_warn_header": "— Advertencias antes del ban —",
    "params_mute_header": "— Duración del silencio (min) —",
    "params_threshold_header": "— Umbral de confianza —",
    "toggle_ignore_admins": "Ignorar admins",
    "toggle_notify": "Notificaciones",
    "toggle_flood": "Detección de flood",
    "duration_day_1": "1 día",
    "duration_days": "{value} días",
    "duration_off": "desactivado",
    "duration_seconds": "{value} s",
    "duration_minutes": "{value} min",
    "duration_hours": "{value} h",
    "params_self_delete": "• Autoborrado de mensajes del bot: {value}",
    "params_self_delete_header": "— Autoborrado de mensajes del bot —",
    "alert_self_delete": "Autoborrado: {value}",
    # Language screen
    "language_title": "🌐 <b>Idioma de la interfaz</b>",
    "language_hint": "<i>Elige el idioma del bot para este chat.</i>",
    # Alerts
    "alert_admins_only": "Solo los administradores pueden cambiar los ajustes.",
    "alert_saved": "Guardado",
    "alert_warn_limit": "Límite de advertencias: {value}",
    "alert_mute": "Silencio: {value} min",
    "alert_threshold": "Umbral: {value}",
    "alert_rights_ok": "Los permisos están bien ✅",
    "alert_rights_missing": "Faltan permisos: «Eliminar mensajes» y «Restringir miembros».",
    "alert_language": "Idioma: {name}",
    # Categories
    "cat_profanity": "Groserías",
    "cat_insult": "Insultos",
    "cat_fraud": "Fraude",
    "cat_bullying": "Acoso",
    "cat_trolling": "Troleo",
    "cat_spam": "Spam",
    "cat_flood": "Flood",
    # Actions
    "action_off": "desactivado",
    "action_auto": "auto",
    "action_warn": "advertir",
    "action_delete": "eliminar",
    "action_mute": "silenciar",
    "action_ban": "banear",
    # Spam types
    "spam_job_offer": "oferta de trabajo",
    "spam_crypto_scam": "estafa cripto",
    "spam_phishing": "phishing/robo de datos",
    "spam_ads": "publicidad/promo",
    "spam_contact_bait": "llamada al privado",
    "spam_other": "otro",
    # Heuristics
    "heur_repost_chats": "reenviado a {count} chats",
    "heur_repost_second": "mismo texto en un segundo chat",
    "heur_repeat_msg": "mensaje repetido",
    "heur_many_links": "muchos enlaces en una oferta de trabajo",
    "heur_rules": "reglas",
    # Command menu
    "cmd_settings": "Ajustes de moderación",
    "cmd_stats": "Estadísticas de infracciones",
    "cmd_check": "Analizar un texto",
    "cmd_warn": "Advertir a un miembro (respondiendo)",
    "cmd_unwarn": "Quitar advertencias (respondiendo)",
    "cmd_resetwarns": "Reiniciar advertencias (respondiendo)",
    "cmd_help": "Ayuda",
}

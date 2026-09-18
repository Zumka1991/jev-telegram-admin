"""Strings em português (Brasil)."""

STRINGS: dict[str, str] = {
    # General
    "start": (
        "Olá! Eu sou o <b>Jev</b>, um moderador com IA.\n"
        "Adicione-me a um grupo e conceda as permissões <i>Excluir mensagens</i> e "
        "<i>Restringir membros</i>, e eu vou manter a ordem.\n\n"
    ),
    "help": (
        "<b>Jev — moderador de grupos com IA</b>\n\n"
        "Eu leio as mensagens e uso o modelo <b>Jev</b> (TypeSafe System One) para "
        "detectar palavrões, insultos, fraude, bullying, trolling e spam; depois "
        "excluo a mensagem, silencio ou baneo — conforme configurado pelos admins.\n\n"
        "<b>Comandos</b>\n"
        "/settings — configurações deste chat (botões)\n"
        "/stats — estatísticas de infrações (7 dias)\n"
        "/warn — advertir um membro (respondendo)\n"
        "/unwarn — remover advertências (respondendo)\n"
        "/resetwarns — zerar advertências (respondendo)\n"
        "/check — analisar um texto sem agir\n"
        "/help — esta ajuda\n\n"
        "Adicione-me a um grupo e conceda permissões: excluir mensagens e restringir membros."
    ),
    "no_rights": (
        "⚠️ Não tenho as permissões necessárias. Conceda-me: "
        "<i>excluir mensagens</i> e <i>restringir membros</i>."
    ),
    "group_only": "Este comando funciona em um grupo. Adicione-me a um grupo e conceda as permissões.",
    "admins_only": "⛔ Este comando está disponível apenas para administradores do chat.",
    "reply_required": "Responda com {command} à mensagem de um membro.",
    "cannot_warn_admin": "Você não pode advertir um administrador.",
    # Warnings
    "warn_given": "⚠️ {mention}, advertência {count}/{limit}.",
    "warn_ban": "⛔ {mention} foi banido: limite de advertências ({limit}) atingido.",
    "no_warnings": "{mention} não tem advertências.",
    "unwarn_done": "✅ Todas as advertências de {mention} foram removidas.",
    "reset_done": "✅ Advertências zeradas para {mention}.",
    # Check
    "check_usage": "Uso: <code>/check texto para analisar</code>",
    "check_title": "<b>🔎 Análise de texto</b>",
    "check_severity": "Gravidade: {value}/4",
    "check_spam_type": "Tipo de spam: {type}",
    "check_recommendation": "Recomendação do Jev: <b>{action}</b>{extra}",
    "check_evidence": "Sinais: {list}",
    "check_model": "<i>Modelo: {model}</i>",
    # Stats
    "stats_title": "<b>📊 Estatísticas de moderação (7 dias)</b>",
    "stats_empty": "Nenhuma infração registrada.",
    "stats_total": "Total de infrações: <b>{total}</b>",
    "stats_top": "<b>Maiores infratores</b>",
    # Violations
    "violation_warn": "⚠️ {mention}, advertência {warnings}/{limit}: <b>{label}</b>{detail}.",
    "violation_delete": "🗑️ {mention}, mensagem excluída: <b>{label}</b>{detail}.",
    "violation_mute": "🔇 {mention} foi silenciado por <b>{minutes} min</b>: <b>{label}</b>{detail}.",
    "violation_ban": "⛔ {mention} foi banido: <b>{label}</b>{detail}.",
    "warn_limit_reached": "Limite de advertências ({limit}) atingido.",
    # Settings menu
    "settings_chat": "<b>Chat:</b> {title}",
    "settings_moderation": "<b>Moderação:</b> {status}",
    "settings_threshold": "<b>Limite:</b> {value}",
    "settings_warn_limit": "<b>Advertências até o ban:</b> {value}",
    "settings_mute": "<b>Duração do silêncio:</b> {value} min",
    "settings_hint": "<i>Toque em uma categoria para escolher uma ação.</i>",
    "status_on": "ativada",
    "status_off": "desativada",
    "btn_moderation": "Moderação: {status}",
    "btn_params": "⚙️ Parâmetros",
    "btn_check_rights": "🩺 Verificar permissões do bot",
    "btn_refresh": "🔄 Atualizar",
    "btn_back": "⬅️ Voltar",
    "btn_language": "🌐 Idioma",
    # Category screen
    "category_title": "{emoji} <b>{label}</b>",
    "category_threshold": "<b>Limite de confiança:</b> {value}",
    "category_flood_threshold": "<b>Limite de flood:</b> {messages} mensagens / {seconds} s",
    "category_current": "<b>Ação atual:</b> {action}",
    "category_hint": (
        "<i>off — ignorar, auto — o bot decide (excluir/silenciar/banir) pela "
        "gravidade, warn — advertir, delete — excluir, mute — silenciar, ban — banir.</i>"
    ),
    # Parameters screen
    "params_title": "<b>⚙️ Parâmetros</b>",
    "params_ignore_admins": "• Ignorar admins: {value}",
    "params_notify": "• Notificações: {value}",
    "params_flood": "• Detecção de flood: {value}",
    "params_warn_limit": "• Advertências até o ban: {value}",
    "params_mute": "• Duração do silêncio: {value} min",
    "params_threshold": "• Limite de confiança do modelo: {value}",
    "params_yes": "sim",
    "params_no": "não",
    "params_warn_header": "— Advertências até o ban —",
    "params_mute_header": "— Duração do silêncio (min) —",
    "params_threshold_header": "— Limite de confiança —",
    "toggle_ignore_admins": "Ignorar admins",
    "toggle_notify": "Notificações",
    "toggle_flood": "Detecção de flood",
    "duration_day_1": "1 dia",
    "duration_days": "{value} dias",
    "duration_off": "desativado",
    "duration_seconds": "{value} s",
    "duration_minutes": "{value} min",
    "duration_hours": "{value} h",
    "params_self_delete": "• Exclusão automática das mensagens do bot: {value}",
    "params_self_delete_header": "— Exclusão automática das mensagens do bot —",
    "alert_self_delete": "Exclusão automática: {value}",
    # Language screen
    "language_title": "🌐 <b>Idioma da interface</b>",
    "language_hint": "<i>Escolha o idioma do bot para este chat.</i>",
    # Alerts
    "alert_admins_only": "Apenas administradores podem alterar as configurações.",
    "alert_saved": "Salvo",
    "alert_warn_limit": "Limite de advertências: {value}",
    "alert_mute": "Silêncio: {value} min",
    "alert_threshold": "Limite: {value}",
    "alert_rights_ok": "Permissões OK ✅",
    "alert_rights_missing": "Faltam permissões: «Excluir mensagens» e «Restringir membros».",
    "alert_language": "Idioma: {name}",
    # Categories
    "cat_profanity": "Palavrões",
    "cat_insult": "Insultos",
    "cat_fraud": "Fraude",
    "cat_bullying": "Bullying",
    "cat_trolling": "Trolling",
    "cat_spam": "Spam",
    "cat_flood": "Flood",
    # Actions
    "action_off": "desativado",
    "action_auto": "auto",
    "action_warn": "advertir",
    "action_delete": "excluir",
    "action_mute": "silenciar",
    "action_ban": "banir",
    # Spam types
    "spam_job_offer": "oferta de emprego",
    "spam_crypto_scam": "golpe de cripto",
    "spam_phishing": "phishing/roubo de dados",
    "spam_ads": "anúncios/promo",
    "spam_contact_bait": "chamada para o privado",
    "spam_other": "outro",
    # Heuristics
    "heur_repost_chats": "reenviado para {count} chats",
    "heur_repost_second": "mesmo texto em um segundo chat",
    "heur_repeat_msg": "mensagem repetida",
    "heur_many_links": "muitos links em uma oferta de emprego",
    "heur_rules": "regras",
    # Command menu
    "cmd_settings": "Configurações de moderação",
    "cmd_stats": "Estatísticas de infrações",
    "cmd_check": "Analisar um texto",
    "cmd_warn": "Advertir um membro (respondendo)",
    "cmd_unwarn": "Remover advertências (respondendo)",
    "cmd_resetwarns": "Zerar advertências (respondendo)",
    "cmd_help": "Ajuda",
}

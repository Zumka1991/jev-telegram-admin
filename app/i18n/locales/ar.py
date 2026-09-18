"""سلاسل بالعربية."""

STRINGS: dict[str, str] = {
    # General
    "start": (
        "مرحبًا! أنا <b>Jev</b>، مشرف بالذكاء الاصطناعي.\n"
        "أضِفني إلى مجموعة وامنحني صلاحيتي <i>حذف الرسائل</i> و"
        "<i>تقييد الأعضاء</i>، وسأحافظ على النظام.\n\n"
    ),
    "help": (
        "<b>Jev — مشرف المجموعات بالذكاء الاصطناعي</b>\n\n"
        "أقرأ الرسائل وأستخدم نموذج <b>Jev</b> (TypeSafe System One) لكشف "
        "الشتائم والإهانات والاحتيال والتنمّر والاستفزاز والرسائل المزعجة، "
        "ثم أحذف الرسالة أو أكتم أو أحظر العضو — حسب إعدادات المشرفين.\n\n"
        "<b>الأوامر</b>\n"
        "/settings — إعدادات هذه المجموعة (أزرار)\n"
        "/stats — إحصاءات المخالفات لآخر 7 أيام\n"
        "/warn — تحذير عضو (بالرد)\n"
        "/unwarn — إزالة التحذيرات (بالرد)\n"
        "/resetwarns — تصفير التحذيرات (بالرد)\n"
        "/check — فحص نص دون اتخاذ إجراء\n"
        "/help — هذه المساعدة\n\n"
        "أضِفني إلى مجموعة وامنحني الصلاحيات: حذف الرسائل وتقييد الأعضاء."
    ),
    "no_rights": (
        "⚠️ لا أملك الصلاحيات المطلوبة. امنحني: "
        "<i>حذف الرسائل</i> و<i>تقييد الأعضاء</i>."
    ),
    "group_only": "هذا الأمر يعمل داخل مجموعة. أضِفني إلى مجموعة وامنحني الصلاحيات.",
    "admins_only": "⛔ هذا الأمر متاح لمشرفي المجموعة فقط.",
    "reply_required": "ردّ بالأمر {command} على رسالة العضو.",
    "cannot_warn_admin": "لا يمكنك تحذير مشرف.",
    # Warnings
    "warn_given": "⚠️ {mention}، تحذير {count}/{limit}.",
    "warn_ban": "⛔ تم حظر {mention}: بلغ حد التحذيرات ({limit}).",
    "no_warnings": "لا توجد تحذيرات لدى {mention}.",
    "unwarn_done": "✅ تمت إزالة جميع تحذيرات {mention}.",
    "reset_done": "✅ تم تصفير تحذيرات {mention}.",
    # Check
    "check_usage": "الاستخدام: <code>/check النص المراد فحصه</code>",
    "check_title": "<b>🔎 فحص النص</b>",
    "check_severity": "الخطورة: {value}/4",
    "check_spam_type": "نوع الإزعاج: {type}",
    "check_recommendation": "توصية Jev: <b>{action}</b>{extra}",
    "check_evidence": "المؤشرات: {list}",
    "check_model": "<i>النموذج: {model}</i>",
    # Stats
    "stats_title": "<b>📊 إحصاءات الإشراف لآخر 7 أيام</b>",
    "stats_empty": "لم تُسجَّل أي مخالفة.",
    "stats_total": "إجمالي المخالفات: <b>{total}</b>",
    "stats_top": "<b>أكثر المخالفين</b>",
    # Violations
    "violation_warn": "⚠️ {mention}، تحذير {warnings}/{limit}: <b>{label}</b>{detail}.",
    "violation_delete": "🗑️ {mention}، تم حذف الرسالة: <b>{label}</b>{detail}.",
    "violation_mute": "🔇 تم كتم {mention} لمدة <b>{minutes} دقيقة</b>: <b>{label}</b>{detail}.",
    "violation_ban": "⛔ تم حظر {mention}: <b>{label}</b>{detail}.",
    "warn_limit_reached": "بلغ حد التحذيرات ({limit}).",
    # Settings menu
    "settings_chat": "<b>المجموعة:</b> {title}",
    "settings_moderation": "<b>الإشراف:</b> {status}",
    "settings_threshold": "<b>الحد:</b> {value}",
    "settings_warn_limit": "<b>التحذيرات قبل الحظر:</b> {value}",
    "settings_mute": "<b>مدة الكتم:</b> {value} دقيقة",
    "settings_hint": "<i>اضغط على فئة لاختيار الإجراء.</i>",
    "status_on": "مفعّل",
    "status_off": "معطّل",
    "btn_moderation": "الإشراف: {status}",
    "btn_params": "⚙️ الإعدادات",
    "btn_check_rights": "🩺 فحص صلاحيات البوت",
    "btn_refresh": "🔄 تحديث",
    "btn_back": "⬅️ رجوع",
    "btn_language": "🌐 اللغة",
    # Category screen
    "category_title": "{emoji} <b>{label}</b>",
    "category_threshold": "<b>حد الثقة:</b> {value}",
    "category_flood_threshold": "<b>حد الإغراق:</b> {messages} رسائل / {seconds} ثانية",
    "category_current": "<b>الإجراء الحالي:</b> {action}",
    "category_hint": (
        "<i>off — تجاهل، auto — يقرّر البوت (حذف/كتم/حظر) حسب الخطورة، "
        "warn — تحذير، delete — حذف، mute — كتم، ban — حظر.</i>"
    ),
    # Parameters screen
    "params_title": "<b>⚙️ الإعدادات</b>",
    "params_ignore_admins": "• تجاهل المشرفين: {value}",
    "params_notify": "• الإشعارات: {value}",
    "params_flood": "• كشف الإغراق: {value}",
    "params_warn_limit": "• التحذيرات قبل الحظر: {value}",
    "params_mute": "• مدة الكتم: {value} دقيقة",
    "params_threshold": "• حد ثقة النموذج: {value}",
    "params_yes": "نعم",
    "params_no": "لا",
    "params_warn_header": "— التحذيرات قبل الحظر —",
    "params_mute_header": "— مدة الكتم (دقيقة) —",
    "params_threshold_header": "— حد الثقة —",
    "toggle_ignore_admins": "تجاهل المشرفين",
    "toggle_notify": "الإشعارات",
    "toggle_flood": "كشف الإغراق",
    "duration_day_1": "يوم واحد",
    "duration_days": "{value} أيام",
    "duration_off": "معطّل",
    "duration_seconds": "{value} ثانية",
    "duration_minutes": "{value} دقيقة",
    "duration_hours": "{value} ساعة",
    "params_self_delete": "• الحذف التلقائي لرسائل البوت: {value}",
    "params_self_delete_header": "— الحذف التلقائي لرسائل البوت —",
    "alert_self_delete": "الحذف التلقائي: {value}",
    # Language screen
    "language_title": "🌐 <b>لغة الواجهة</b>",
    "language_hint": "<i>اختر لغة البوت لهذه المجموعة.</i>",
    # Alerts
    "alert_admins_only": "يمكن للمشرفين فقط تغيير الإعدادات.",
    "alert_saved": "تم الحفظ",
    "alert_warn_limit": "حد التحذيرات: {value}",
    "alert_mute": "الكتم: {value} دقيقة",
    "alert_threshold": "الحد: {value}",
    "alert_rights_ok": "الصلاحيات سليمة ✅",
    "alert_rights_missing": "صلاحيات ناقصة: «حذف الرسائل» و«تقييد الأعضاء».",
    "alert_language": "اللغة: {name}",
    # Categories
    "cat_profanity": "الشتائم",
    "cat_insult": "الإهانات",
    "cat_fraud": "الاحتيال",
    "cat_bullying": "التنمّر",
    "cat_trolling": "الاستفزاز",
    "cat_spam": "الرسائل المزعجة",
    "cat_flood": "الإغراق",
    # Actions
    "action_off": "معطّل",
    "action_auto": "تلقائي",
    "action_warn": "تحذير",
    "action_delete": "حذف",
    "action_mute": "كتم",
    "action_ban": "حظر",
    # Spam types
    "spam_job_offer": "عرض عمل",
    "spam_crypto_scam": "احتيال عملات رقمية",
    "spam_phishing": "تصيّد/سرقة بيانات",
    "spam_ads": "إعلانات/ترويج",
    "spam_contact_bait": "دعوة للخاص",
    "spam_other": "أخرى",
    # Heuristics
    "heur_repost_chats": "أُرسل إلى {count} مجموعات",
    "heur_repost_second": "النص نفسه في مجموعة أخرى",
    "heur_repeat_msg": "رسالة مكرّرة",
    "heur_many_links": "روابط كثيرة في عرض عمل",
    "heur_rules": "قواعد",
    # Command menu
    "cmd_settings": "إعدادات الإشراف",
    "cmd_stats": "إحصاءات المخالفات",
    "cmd_check": "فحص نص",
    "cmd_warn": "تحذير عضو (بالرد)",
    "cmd_unwarn": "إزالة التحذيرات (بالرد)",
    "cmd_resetwarns": "تصفير التحذيرات (بالرد)",
    "cmd_help": "المساعدة",
}

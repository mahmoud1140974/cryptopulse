"""Arabic strings for CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Welcome / menu
    "welcome": (
        "👋 <b>مرحبا بك في CryptoPulse</b>\n\n"
        "افحص الرموز الرقمية، تابع مؤشرات المخاطر، واستقبل تنبيهات السوق.\n\n"
        "اختر خياراً من الأسفل."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nاختر خياراً من الأسفل.",
    "choose_language": "🌍 <b>الرجاء اختيار اللغة:</b>",
    "language_set": "✅ تم ضبط اللغة على <b>العربية</b>.",

    # Main menu buttons
    "btn_scan": "🔍 فحص رمز",
    "btn_wallet": "👛 تحليل محفظة",
    "btn_market": "📊 السوق",
    "btn_trending": "🔥 الأكثر رواجاً",
    "btn_whales": "🐋 الحيتان",
    "btn_alerts": "🔔 التنبيهات",
    "btn_watchlist": "⭐ قائمة المتابعة",
    "btn_news": "📰 الأخبار",
    "btn_premium": "💎 بريميوم",
    "btn_settings": "⚙️ الإعدادات",
    "btn_help": "❓ مساعدة",
    "btn_back": "⬅️ رجوع",
    "btn_refresh": "🔄 تحديث",
    "btn_track": "⭐ متابعة",
    "btn_tracked": "⭐ متابَع",
    "btn_set_alert": "🔔 ضبط تنبيه",

    # Scan
    "scan_prompt": (
        "🔍 أرسل لي عنوان العقد الخاص بالرمز الذي تريد فحصه.\n\n"
        "أمثلة: عنوان EVM يبدأ بـ 0x، أو عنوان Solana base58."
    ),
    "scan_invalid_address": "❌ عنوان غير صالح. {reason}",
    "scan_unavailable": "⚠️ بعض بيانات السوق غير متوفرة مؤقتاً. حاول مرة أخرى.",
    "scan_limit_free_reached": (
        "⚠️ <b>لقد وصلت إلى الحد الشهري</b>\n\n"
        "لقد استخدمت <b>{used}/{limit}</b> عمليات فحص مجانية هذا الشهر.\n\n"
        "قم بالترقية للاستمرار:\n"
        "⭐ <b>Pro</b> — 50 عملية فحص يومياً بحوالي 5$/شهر\n"
        "👑 <b>Premium</b> — عمليات فحص غير محدودة بحوالي 15$/شهر\n\n"
        "استخدم /subscribe لعرض جميع الخطط."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>تم الوصول إلى الحد اليومي</b>\n\n"
        "لقد استخدمت <b>{used}/{limit}</b> عملية فحص اليوم.\n\n"
        "عد غداً، أو قم بالترقية إلى Premium لفحوصات غير محدودة.\n\n"
        "استخدم /subscribe لعرض جميع الخطط."
    ),

    # Scan report
    "report_reasons": "📋 <b>الأسباب</b>",
    "report_market_data": "📊 <b>بيانات السوق</b>",
    "report_price": "💵 <b>السعر:</b> {value}",
    "report_liquidity": "💧 <b>السيولة:</b> {value} $",
    "report_volume": "📈 <b>حجم 24س:</b> {value} $",
    "report_market_cap": "🏦 <b>القيمة السوقية:</b> {value} $",
    "report_holders": "👥 <b>الحاملون:</b> {value}",
    "report_chain": "⛓ <b>الشبكة:</b> {value}",
    "report_honeypot_yes": "🍯 <b>Honeypot:</b> نعم 🚨 لا تتداول",
    "report_honeypot_no": "🍯 <b>Honeypot:</b> لا ✅",
    "report_taxes": "💰 <b>ضريبة الشراء/البيع:</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>الملكية:</b> تم التنازل ✅",
    "report_ownership_not_renounced": "👑 <b>الملكية:</b> لم يتم التنازل ⚠️ (المالك: {owner})",
    "report_freeze_active": "🥶 <b>سلطة التجميد:</b> نشطة ⚠️",
    "report_freeze_disabled": "🥶 <b>سلطة التجميد:</b> معطلة ✅",
    "report_disclaimer": (
        "\n⚠️ <i>الأصول الرقمية عالية الخطورة. قم دائماً بأبحاثك الخاصة قبل التداول.</i>"
    ),

    # New: supply, decimals, links
    "report_supply": "💰 <b>إجمالي العرض:</b> {value}",
    "report_decimals": "🔢 <b>المنازل العشرية:</b> {value}",
    "report_links": "🔗 <b>الروابط</b>",
    "report_link_website": "🌐 الموقع",
    "report_link_twitter": "🐦 تويتر",
    "report_link_telegram": "📢 تيليجرام",
    "report_link_dexscreener": "📊 DexScreener",

    # Wallet tracking
    "wallet_menu": (
        "👛 <b>أدوات المحفظة</b>\n\n"
        "• <code>/trackwallet &lt;عنوان&gt;</code> — متابعة محفظة\n"
        "• <code>/mywallets</code> — عرض محافظك المتابَعة\n"
        "• <code>/checkwallet &lt;عنوان&gt;</code> — عرض النشاط الأخير\n"
        "• <code>/untrackwallet &lt;عنوان&gt;</code> — إزالة محفظة"
    ),
    "wallet_usage_track": (
        "👛 <b>متابعة محفظة</b>\n\n"
        "الاستخدام: <code>/trackwallet &lt;عنوان&gt; [شبكة]</code>\n\n"
        "أمثلة:\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "الاستخدام: <code>/untrackwallet &lt;عنوان&gt; [شبكة]</code>",
    "wallet_usage_check": "الاستخدام: <code>/checkwallet &lt;عنوان&gt; [شبكة]</code>",
    "wallet_added": (
        "✅ <b>تمت إضافة المحفظة إلى قائمة المتابعة.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ الشبكة: <b>{chain}</b>\n"
        "📊 المتابَع: <b>{count}/{limit}</b>\n\n"
        "سيتم تنبيهك عندما تقوم هذه المحفظة بأي حركة.\n"
        "اعرض قائمتك باستخدام /mywallets."
    ),
    "wallet_removed": "🗑 تمت إزالة <code>{address}</code> من محافظك المتابَعة.",
    "wallet_list_empty": (
        "👛 <b>محافظك المتابَعة</b>\n\n"
        "لا توجد محافظ بعد.\n\n"
        "أضف واحدة باستخدام <code>/trackwallet &lt;عنوان&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>محافظك المتابَعة</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nاستخدم /checkwallet &lt;عنوان&gt; لعرض النشاط الأخير.\n"
        "أزل واحدة باستخدام /untrackwallet &lt;عنوان&gt;."
    ),
    "wallet_check_fetching": "⏳ جاري جلب المعاملات الأخيرة…",
    "wallet_check_no_data": (
        "⚠️ لا توجد معاملات حديثة لـ <code>{address}</code>\n"
        "الشبكة: <b>{chain}</b>\n\n"
        "إما أن المحفظة غير نشطة، أو أن مزود البيانات غير متوفر مؤقتاً."
    ),
    "wallet_check_header": "👛 <b>نشاط المحفظة</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ الشبكة: <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>المصدر: Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>متابعة المحافظ ميزة Pro و Premium.</b>\n\n"
        "تابع محافظ الأموال الذكية واستقبل تنبيهات عند أي حركة.\n\n"
        "⭐ <b>Pro</b> — حتى 3 محافظ (~5$/شهر)\n"
        "👑 <b>Premium</b> — حتى 20 محفظة (~15$/شهر)\n\n"
        "استخدم /subscribe لعرض جميع الخطط."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>تم الوصول إلى حد المحافظ</b>\n\n"
        "أنت تتابع <b>{count}/{limit}</b> محفظة.\n\n"
        "أزل واحدة باستخدام /untrackwallet أو قم بالترقية.\n\n"
        "استخدم /subscribe لعرض جميع الخطط."
    ),

    # Watchlist
    "watchlist_empty": "⭐ <b>قائمة المتابعة</b>\n\nلا توجد رموز بعد. استخدم /track &lt;عنوان&gt; لإضافة واحد.",
    "watchlist_header": "⭐ <b>قائمة المتابعة</b> — {count} رمز\n",
    "watchlist_added": "✅ تمت إضافة <b>{symbol}</b> إلى قائمتك.",
    "watchlist_removed": "🗑 تمت الإزالة من قائمتك.",
    "watchlist_limit_reached": (
        "⚠️ <b>تم الوصول إلى حد القائمة</b>\n\n"
        "أنت تتابع <b>{count}/{limit}</b> رمز.\n\n"
        "قم بالترقية لإضافة المزيد.\n\n"
        "استخدم /subscribe لعرض جميع الخطط."
    ),

    # Alerts
    "alerts_empty": (
        "🔔 <b>التنبيهات</b>\n\n"
        "لا توجد تنبيهات بعد. تابع رمزاً وسينبهك CryptoPulse عندما:\n"
        "• يتغير السعر بأكثر من 10%\n"
        "• تتغير السيولة بأكثر من 20%\n"
        "• يتجاوز حجم 24س 3 أضعاف المتوسط"
    ),
    "alerts_header": "🔔 <b>تنبيهاتك الأخيرة</b>\n",

    # Market / prices
    "market_header": "📊 <b>نظرة عامة على السوق</b>\n\n",
    "market_total_cap": "القيمة السوقية الإجمالية: {value}",
    "market_btc_dominance": "هيمنة BTC: {value}",
    "prices_header": "💹 <b>أفضل 10 عملات رقمية</b>",
    "prices_subheader": "<i>حسب القيمة السوقية (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ لا يمكن جلب الأسعار الآن. حاول بعد دقيقة.",

    # Subscription
    "subscribe_title": "💎 <b>خطط CryptoPulse</b>\n",
    "mysubscription_title": "👤 <b>اشتراكك</b>\n\n",
    "mysubscription_plan": "الخطة: <b>{plan}</b>",
    "mysubscription_price": "السعر: {price}",
    "mysubscription_expires": "⏰ ينتهي في: <b>{date}</b>",
    "mysubscription_limits": "\n<b>الحدود الحالية:</b>",
    "mysubscription_use": "\nاستخدم /subscribe لعرض خيارات الترقية.",

    # Help
    "help_title": "❓ <b>مساعدة CryptoPulse</b>\n",
    "help_section_analysis": "<b>🔍 تحليل الرموز</b>",
    "help_section_market": "<b>📊 السوق &amp; البيانات</b>",
    "help_section_sub": "<b>💎 الاشتراك</b>",
    "help_section_other": "<b>❓ أخرى</b>",
    "help_supported_chains": "<b>الشبكات المدعومة</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>الأصول الرقمية عالية الخطورة. توفر هذه الأداة بيانات ومؤشرات "
        "للمخاطر لأغراض إعلامية فقط ولا تشكل نصيحة مالية.</i>"
    ),

    # Generic
    "feature_coming_soon": "هذه الميزة قادمة قريباً.",
    "data_unavailable": "البيانات غير متوفرة.",
    "not_financial_advice": "⚠️ ليست نصيحة مالية.",
    "unknown_plan": "خطة غير معروفة.",
    "error_generic": "⚠️ حدث خطأ. حاول مرة أخرى.",

    # Payment
    "payment_success": (
        "🎉 <b>مرحباً بك في CryptoPulse {plan}!</b>\n\n"
        "اشتراكك نشط الآن.\n"
        "⏰ ينتهي في: <b>{date}</b>\n"
        "⭐ النجوم المدفوعة: {stars}\n\n"
        "استخدم /mysubscription لعرض خطتك."
    ),
    "payment_unknown_plan": (
        "✅ تم استلام الدفع، لكن تعذّر تحديد الخطة. "
        "تواصل مع الدعم مع معرف الدفع."
    ),
    "payment_activation_failed": (
        "✅ تم استلام الدفع لكن فشل التفعيل. "
        "تواصل مع الدعم مع معرف المعاملة."
    ),
    "payment_cancel": "⚠️ تعذر بدء الدفع. حاول بعد لحظات.",
}

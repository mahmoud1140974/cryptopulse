"""Russian strings for CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Welcome / menu
    "welcome": (
        "👋 <b>Добро пожаловать в CryptoPulse</b>\n\n"
        "Анализируйте крипто-токены, следите за индикаторами риска и получайте рыночные оповещения.\n\n"
        "Выберите опцию ниже."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nВыберите опцию ниже.",
    "choose_language": "🌍 <b>Пожалуйста, выберите язык:</b>",
    "language_set": "✅ Язык установлен на <b>Русский</b>.",

    # Main menu buttons
    "btn_scan": "🔍 Сканировать токен",
    "btn_wallet": "👛 Анализ кошелька",
    "btn_market": "📊 Рынок",
    "btn_trending": "🔥 В тренде",
    "btn_whales": "🐋 Киты",
    "btn_alerts": "🔔 Оповещения",
    "btn_watchlist": "⭐ Список наблюдения",
    "btn_news": "📰 Новости",
    "btn_premium": "💎 Премиум",
    "btn_settings": "⚙️ Настройки",
    "btn_help": "❓ Помощь",
    "btn_back": "⬅️ Назад",
    "btn_refresh": "🔄 Обновить",
    "btn_track": "⭐ Отслеживать",
    "btn_tracked": "⭐ Отслеживается",
    "btn_set_alert": "🔔 Создать оповещение",

    # Scan
    "scan_prompt": (
        "🔍 Отправьте мне адрес контракта токена для анализа.\n\n"
        "Примеры: адрес EVM, начинающийся с 0x, или адрес Solana base58."
    ),
    "scan_invalid_address": "❌ Неверный адрес. {reason}",
    "scan_unavailable": "⚠️ Некоторые рыночные данные временно недоступны. Попробуйте снова.",
    "scan_limit_free_reached": (
        "⚠️ <b>Вы достигли месячного лимита</b>\n\n"
        "Вы использовали <b>{used}/{limit}</b> бесплатных сканирований в этом месяце.\n\n"
        "Обновите план, чтобы продолжить:\n"
        "⭐ <b>Pro</b> — 50 сканирований/день за ~$5/мес\n"
        "👑 <b>Premium</b> — Неограниченные сканирования за ~$15/мес\n\n"
        "Используйте /subscribe для просмотра планов."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>Достигнут дневной лимит</b>\n\n"
        "Вы использовали <b>{used}/{limit}</b> сканирований сегодня.\n\n"
        "Вернитесь завтра или перейдите на Premium.\n\n"
        "Используйте /subscribe для просмотра планов."
    ),

    # Scan report
    "report_reasons": "📋 <b>Причины</b>",
    "report_market_data": "📊 <b>Рыночные данные</b>",
    "report_price": "💵 <b>Цена:</b> {value}",
    "report_liquidity": "💧 <b>Ликвидность:</b> {value} $",
    "report_volume": "📈 <b>Объём 24ч:</b> {value} $",
    "report_market_cap": "🏦 <b>Кап.:</b> {value} $",
    "report_holders": "👥 <b>Держатели:</b> {value}",
    "report_chain": "⛓ <b>Сеть:</b> {value}",
    "report_honeypot_yes": "🍯 <b>Honeypot:</b> ДА 🚨 НЕ ТОРГУЙТЕ",
    "report_honeypot_no": "🍯 <b>Honeypot:</b> Нет ✅",
    "report_taxes": "💰 <b>Налог покупки/продажи:</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>Владение:</b> Отказано ✅",
    "report_ownership_not_renounced": "👑 <b>Владение:</b> НЕ отказано ⚠️ (владелец: {owner})",
    "report_freeze_active": "🥶 <b>Право заморозки:</b> Активно ⚠️",
    "report_freeze_disabled": "🥶 <b>Право заморозки:</b> Отключено ✅",
    "report_disclaimer": (
        "\n⚠️ <i>Крипто-активы крайне рискованны. Всегда проводите собственное исследование перед торговлей.</i>"
    ),

    # Wallet tracking
    "wallet_menu": (
        "👛 <b>Инструменты кошелька</b>\n\n"
        "• <code>/trackwallet &lt;адрес&gt;</code> — отслеживать кошелёк\n"
        "• <code>/mywallets</code> — список отслеживаемых\n"
        "• <code>/checkwallet &lt;адрес&gt;</code> — последняя активность\n"
        "• <code>/untrackwallet &lt;адрес&gt;</code> — удалить кошелёк"
    ),
    "wallet_usage_track": (
        "👛 <b>Отслеживать кошелёк</b>\n\n"
        "Использование: <code>/trackwallet &lt;адрес&gt; [сеть]</code>\n\n"
        "Примеры:\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "Использование: <code>/untrackwallet &lt;адрес&gt; [сеть]</code>",
    "wallet_usage_check": "Использование: <code>/checkwallet &lt;адрес&gt; [сеть]</code>",
    "wallet_added": (
        "✅ <b>Кошелёк добавлен в список отслеживания.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ Сеть: <b>{chain}</b>\n"
        "📊 Отслеживается: <b>{count}/{limit}</b>\n\n"
        "Вы получите оповещение, когда кошелёк совершит движение.\n"
        "Просмотр списка: /mywallets."
    ),
    "wallet_removed": "🗑 <code>{address}</code> удалён из отслеживаемых.",
    "wallet_list_empty": (
        "👛 <b>Отслеживаемые кошельки</b>\n\n"
        "Пока нет кошельков.\n\n"
        "Добавьте один: <code>/trackwallet &lt;адрес&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>Отслеживаемые кошельки</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nИспользуйте /checkwallet &lt;адрес&gt; для активности.\n"
        "Удалить: /untrackwallet &lt;адрес&gt;."
    ),
    "wallet_check_fetching": "⏳ Получение последних транзакций…",
    "wallet_check_no_data": (
        "⚠️ Последние транзакции не найдены для <code>{address}</code>\n"
        "Сеть: <b>{chain}</b>\n\n"
        "Либо кошелёк неактивен, либо провайдер временно недоступен."
    ),
    "wallet_check_header": "👛 <b>Активность кошелька</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ Сеть: <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>Источник: Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>Отслеживание кошельков — функция Pro и Premium.</b>\n\n"
        "Следите за smart money и получайте оповещения о движениях.\n\n"
        "⭐ <b>Pro</b> — до 3 кошельков (~$5/мес)\n"
        "👑 <b>Premium</b> — до 20 кошельков (~$15/мес)\n\n"
        "Используйте /subscribe."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>Достигнут лимит кошельков</b>\n\n"
        "Вы отслеживаете <b>{count}/{limit}</b> кошельков.\n\n"
        "Удалите один: /untrackwallet или обновите план.\n\n"
        "Используйте /subscribe."
    ),

    # Watchlist
    "watchlist_empty": "⭐ <b>Список наблюдения</b>\n\nПока нет токенов. Используйте /track &lt;адрес&gt;.",
    "watchlist_header": "⭐ <b>Список наблюдения</b> — {count} токен(ов)\n",
    "watchlist_added": "✅ <b>{symbol}</b> добавлен в список.",
    "watchlist_removed": "🗑 Удалён из списка.",
    "watchlist_limit_reached": (
        "⚠️ <b>Достигнут лимит списка</b>\n\n"
        "Вы отслеживаете <b>{count}/{limit}</b> токенов.\n\n"
        "Обновите план, чтобы добавить больше.\n\n"
        "Используйте /subscribe."
    ),

    # Alerts
    "alerts_empty": (
        "🔔 <b>Оповещения</b>\n\n"
        "Пока нет оповещений. Отслеживайте токен — CryptoPulse оповестит, когда:\n"
        "• цена изменится более чем на 10%\n"
        "• ликвидность изменится более чем на 20%\n"
        "• объём 24ч превысит 3х среднего"
    ),
    "alerts_header": "🔔 <b>Последние оповещения</b>\n",

    # Market / prices
    "market_header": "📊 <b>Обзор рынка</b>\n\n",
    "market_total_cap": "Общая кап.: {value}",
    "market_btc_dominance": "Доминация BTC: {value}",
    "prices_header": "💹 <b>Топ 10 криптовалют</b>",
    "prices_subheader": "<i>По рыночной капитализации (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ Не удалось получить цены. Попробуйте через минуту.",

    # Subscription
    "subscribe_title": "💎 <b>Планы CryptoPulse</b>\n",
    "mysubscription_title": "👤 <b>Ваша подписка</b>\n\n",
    "mysubscription_plan": "План: <b>{plan}</b>",
    "mysubscription_price": "Цена: {price}",
    "mysubscription_expires": "⏰ Истекает: <b>{date}</b>",
    "mysubscription_limits": "\n<b>Текущие лимиты:</b>",
    "mysubscription_use": "\nИспользуйте /subscribe для обновления.",

    # Help
    "help_title": "❓ <b>Помощь CryptoPulse</b>\n",
    "help_section_analysis": "<b>🔍 Анализ токенов</b>",
    "help_section_market": "<b>📊 Рынок &amp; данные</b>",
    "help_section_sub": "<b>💎 Подписка</b>",
    "help_section_other": "<b>❓ Другое</b>",
    "help_supported_chains": "<b>Поддерживаемые сети</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>Крипто-активы крайне рискованны. Этот инструмент предоставляет данные "
        "и индикаторы риска только в информационных целях и не является финансовым советом.</i>"
    ),

    # Generic
    "feature_coming_soon": "Эта функция скоро появится.",
    "data_unavailable": "Данные недоступны.",
    "not_financial_advice": "⚠️ Не является финансовым советом.",
    "unknown_plan": "Неизвестный план.",
    "error_generic": "⚠️ Что-то пошло не так. Попробуйте снова.",

    # Payment
    "payment_success": (
        "🎉 <b>Добро пожаловать в CryptoPulse {plan}!</b>\n\n"
        "Ваша подписка активна.\n"
        "⏰ Истекает: <b>{date}</b>\n"
        "⭐ Звёзд оплачено: {stars}\n\n"
        "Проверить: /mysubscription."
    ),
    "payment_unknown_plan": (
        "✅ Платёж получен, но план не удалось определить. "
        "Свяжитесь с поддержкой, указав ID платежа."
    ),
    "payment_activation_failed": (
        "✅ Платёж получен, но активация не удалась. "
        "Свяжитесь с поддержкой, указав ID транзакции."
    ),
    "payment_cancel": "⚠️ Не удалось начать оплату. Попробуйте через момент.",
}

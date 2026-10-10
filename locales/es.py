"""Cadenas en español para CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Inicio / menú
    "welcome": (
        "👋 <b>Bienvenido a CryptoPulse</b>\n\n"
        "Analiza tokens cripto, sigue indicadores de riesgo y recibe alertas de mercado.\n\n"
        "Elige una opción a continuación."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nElige una opción a continuación.",
    "choose_language": "🌍 <b>Por favor elige tu idioma:</b>",
    "language_set": "✅ Idioma establecido en <b>Español</b>.",

    # Botones del menú principal
    "btn_scan": "🔍 Escanear token",
    "btn_wallet": "👛 Analizar wallet",
    "btn_market": "📊 Mercado",
    "btn_trending": "🔥 Tendencias",
    "btn_whales": "🐋 Ballenas",
    "btn_alerts": "🔔 Alertas",
    "btn_watchlist": "⭐ Lista de seguimiento",
    "btn_news": "📰 Noticias",
    "btn_premium": "💎 Premium",
    "btn_settings": "⚙️ Ajustes",
    "btn_help": "❓ Ayuda",
    "btn_back": "⬅️ Atrás",
    "btn_refresh": "🔄 Actualizar",
    "btn_track": "⭐ Seguir",
    "btn_tracked": "⭐ Siguiendo",
    "btn_set_alert": "🔔 Crear alerta",

    # Escaneo
    "scan_prompt": (
        "🔍 Envíame la dirección del contrato del token a analizar.\n\n"
        "Ejemplos: una dirección EVM que comience por 0x, o una dirección Solana base58."
    ),
    "scan_invalid_address": "❌ Dirección inválida. {reason}",
    "scan_unavailable": "⚠️ Algunos datos del mercado no están disponibles temporalmente. Inténtalo de nuevo.",
    "scan_limit_free_reached": (
        "⚠️ <b>Has alcanzado tu límite mensual</b>\n\n"
        "Has usado <b>{used}/{limit}</b> escaneos gratuitos este mes.\n\n"
        "Mejora tu plan para seguir escaneando:\n"
        "⭐ <b>Pro</b> — 50 escaneos/día por ~5 $/mes\n"
        "👑 <b>Premium</b> — Escaneos ilimitados por ~15 $/mes\n\n"
        "Usa /subscribe para ver todos los planes."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>Límite diario alcanzado</b>\n\n"
        "Has usado <b>{used}/{limit}</b> escaneos hoy.\n\n"
        "Vuelve mañana, o mejora a Premium para escaneos ilimitados.\n\n"
        "Usa /subscribe para ver todos los planes."
    ),

    # Reporte de escaneo
    "report_reasons": "📋 <b>Razones</b>",
    "report_market_data": "📊 <b>Datos de mercado</b>",
    "report_price": "💵 <b>Precio:</b> {value}",
    "report_liquidity": "💧 <b>Liquidez:</b> {value} $",
    "report_volume": "📈 <b>Volumen 24h:</b> {value} $",
    "report_market_cap": "🏦 <b>Cap. de mercado:</b> {value} $",
    "report_holders": "👥 <b>Tenedores:</b> {value}",
    "report_chain": "⛓ <b>Cadena:</b> {value}",
    "report_honeypot_yes": "🍯 <b>Honeypot:</b> SÍ 🚨 NO OPERAR",
    "report_honeypot_no": "🍯 <b>Honeypot:</b> No ✅",
    "report_taxes": "💰 <b>Impuesto compra/venta:</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>Propiedad:</b> Renunciada ✅",
    "report_ownership_not_renounced": "👑 <b>Propiedad:</b> NO renunciada ⚠️ (propietario: {owner})",
    "report_freeze_active": "🥶 <b>Autoridad de congelación:</b> Activa ⚠️",
    "report_freeze_disabled": "🥶 <b>Autoridad de congelación:</b> Desactivada ✅",
    "report_disclaimer": (
        "\n⚠️ <i>Los activos cripto son muy riesgosos. Haz siempre tu propia investigación antes de operar.</i>"
    ),

    # Nuevos: supply, decimals, enlaces
    "report_supply": "💰 <b>Suministro total:</b> {value}",
    "report_decimals": "🔢 <b>Decimales:</b> {value}",
    "report_links": "🔗 <b>Enlaces</b>",
    "report_link_website": "🌐 Sitio web",
    "report_link_twitter": "🐦 Twitter",
    "report_link_telegram": "📢 Telegram",
    "report_link_dexscreener": "📊 DexScreener",

    # Seguimiento de wallets
    "wallet_menu": (
        "👛 <b>Herramientas de wallet</b>\n\n"
        "• <code>/trackwallet &lt;dirección&gt;</code> — seguir un wallet\n"
        "• <code>/mywallets</code> — ver tus wallets seguidos\n"
        "• <code>/checkwallet &lt;dirección&gt;</code> — ver actividad reciente\n"
        "• <code>/untrackwallet &lt;dirección&gt;</code> — eliminar un wallet"
    ),
    "wallet_usage_track": (
        "👛 <b>Seguir un wallet</b>\n\n"
        "Uso: <code>/trackwallet &lt;dirección&gt; [cadena]</code>\n\n"
        "Ejemplos:\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "Uso: <code>/untrackwallet &lt;dirección&gt; [cadena]</code>",
    "wallet_usage_check": "Uso: <code>/checkwallet &lt;dirección&gt; [cadena]</code>",
    "wallet_added": (
        "✅ <b>Wallet añadido a tu lista de seguimiento.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ Cadena: <b>{chain}</b>\n"
        "📊 Siguiendo: <b>{count}/{limit}</b>\n\n"
        "Se te alertará cuando este wallet haga un movimiento.\n"
        "Ve tu lista con /mywallets."
    ),
    "wallet_removed": "🗑 <code>{address}</code> eliminado de tus wallets seguidos.",
    "wallet_list_empty": (
        "👛 <b>Tus wallets seguidos</b>\n\n"
        "Aún no hay wallets.\n\n"
        "Añade uno con <code>/trackwallet &lt;dirección&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>Tus wallets seguidos</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nUsa /checkwallet &lt;dirección&gt; para ver actividad reciente.\n"
        "Elimina uno con /untrackwallet &lt;dirección&gt;."
    ),
    "wallet_check_fetching": "⏳ Obteniendo transacciones recientes…",
    "wallet_check_no_data": (
        "⚠️ No se encontraron transacciones recientes para <code>{address}</code>\n"
        "Cadena: <b>{chain}</b>\n\n"
        "O el wallet no tiene actividad, o el proveedor de datos no está disponible temporalmente."
    ),
    "wallet_check_header": "👛 <b>Actividad del wallet</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ Cadena: <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>Fuente: Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>El seguimiento de wallets es una función Pro & Premium.</b>\n\n"
        "Sigue wallets del smart money y recibe alertas cuando hagan movimientos.\n\n"
        "⭐ <b>Pro</b> — hasta 3 wallets (~5 $/mes)\n"
        "👑 <b>Premium</b> — hasta 20 wallets (~15 $/mes)\n\n"
        "Usa /subscribe para ver todos los planes."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>Límite de wallets alcanzado</b>\n\n"
        "Estás siguiendo <b>{count}/{limit}</b> wallets.\n\n"
        "Elimina uno con /untrackwallet o mejora tu plan.\n\n"
        "Usa /subscribe para ver todos los planes."
    ),

    # Lista de seguimiento
    "watchlist_empty": "⭐ <b>Tu lista de seguimiento</b>\n\nAún no hay tokens. Usa /track &lt;dirección&gt; para añadir uno.",
    "watchlist_header": "⭐ <b>Tu lista de seguimiento</b> — {count} token(s)\n",
    "watchlist_added": "✅ <b>{symbol}</b> añadido a tu lista.",
    "watchlist_removed": "🗑 Eliminado de tu lista.",
    "watchlist_limit_reached": (
        "⚠️ <b>Límite de lista alcanzado</b>\n\n"
        "Estás siguiendo <b>{count}/{limit}</b> tokens.\n\n"
        "Mejora tu plan para añadir más.\n\n"
        "Usa /subscribe para ver todos los planes."
    ),

    # Alertas
    "alerts_empty": (
        "🔔 <b>Alertas</b>\n\n"
        "Aún no hay alertas. Sigue un token y CryptoPulse te alertará cuando:\n"
        "• el precio cambie más del 10 %\n"
        "• la liquidez cambie más del 20 %\n"
        "• el volumen 24h supere 3x el promedio guardado"
    ),
    "alerts_header": "🔔 <b>Tus alertas recientes</b>\n",

    # Mercado / precios
    "market_header": "📊 <b>Visión del mercado</b>\n\n",
    "market_total_cap": "Cap. total del mercado: {value}",
    "market_btc_dominance": "Dominancia BTC: {value}",
    "prices_header": "💹 <b>Top 10 criptomonedas</b>",
    "prices_subheader": "<i>Por capitalización de mercado (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ No se pudieron obtener los precios. Inténtalo en un minuto.",

    # Suscripción
    "subscribe_title": "💎 <b>Planes CryptoPulse</b>\n",
    "mysubscription_title": "👤 <b>Tu suscripción</b>\n\n",
    "mysubscription_plan": "Plan: <b>{plan}</b>",
    "mysubscription_price": "Precio: {price}",
    "mysubscription_expires": "⏰ Expira el: <b>{date}</b>",
    "mysubscription_limits": "\n<b>Límites actuales:</b>",
    "mysubscription_use": "\nUsa /subscribe para ver opciones de mejora.",

    # Ayuda
    "help_title": "❓ <b>Ayuda de CryptoPulse</b>\n",
    "help_section_analysis": "<b>🔍 Análisis de tokens</b>",
    "help_section_market": "<b>📊 Mercado &amp; datos</b>",
    "help_section_sub": "<b>💎 Suscripción</b>",
    "help_section_other": "<b>❓ Otros</b>",
    "help_supported_chains": "<b>Cadenas soportadas</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>Los activos cripto son muy riesgosos. Esta herramienta proporciona datos "
        "e indicadores de riesgo solo con fines informativos y no constituye asesoramiento financiero.</i>"
    ),

    # Genérico
    "feature_coming_soon": "Esta función llegará pronto.",
    "data_unavailable": "Datos no disponibles.",
    "not_financial_advice": "⚠️ No es asesoramiento financiero.",
    "unknown_plan": "Plan desconocido.",
    "error_generic": "⚠️ Algo salió mal. Inténtalo de nuevo.",

    # Pago
    "payment_success": (
        "🎉 <b>¡Bienvenido a CryptoPulse {plan}!</b>\n\n"
        "Tu suscripción está activa.\n"
        "⏰ Expira el: <b>{date}</b>\n"
        "⭐ Estrellas pagadas: {stars}\n\n"
        "Usa /mysubscription para ver tu plan."
    ),
    "payment_unknown_plan": (
        "✅ Pago recibido, pero no se pudo identificar el plan. "
        "Contacta con soporte con tu ID de pago."
    ),
    "payment_activation_failed": (
        "✅ Pago recibido pero la activación falló. "
        "Contacta con soporte con tu ID de transacción."
    ),
    "payment_cancel": "⚠️ No se pudo iniciar el pago. Inténtalo en un momento.",
}

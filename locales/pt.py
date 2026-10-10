"""Cadeias em português para CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Welcome / menu
    "welcome": (
        "👋 <b>Bem-vindo ao CryptoPulse</b>\n\n"
        "Analise tokens cripto, acompanhe indicadores de risco e receba alertas de mercado.\n\n"
        "Escolha uma opção abaixo."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nEscolha uma opção abaixo.",
    "choose_language": "🌍 <b>Por favor, escolha seu idioma:</b>",
    "language_set": "✅ Idioma definido para <b>Português</b>.",

    # Main menu buttons
    "btn_scan": "🔍 Escanear token",
    "btn_wallet": "👛 Analisar carteira",
    "btn_market": "📊 Mercado",
    "btn_trending": "🔥 Em alta",
    "btn_whales": "🐋 Baleias",
    "btn_alerts": "🔔 Alertas",
    "btn_watchlist": "⭐ Lista de acompanhamento",
    "btn_news": "📰 Notícias",
    "btn_premium": "💎 Premium",
    "btn_settings": "⚙️ Configurações",
    "btn_help": "❓ Ajuda",
    "btn_back": "⬅️ Voltar",
    "btn_refresh": "🔄 Atualizar",
    "btn_track": "⭐ Acompanhar",
    "btn_tracked": "⭐ Acompanhado",
    "btn_set_alert": "🔔 Criar alerta",

    # Scan
    "scan_prompt": (
        "🔍 Envie-me o endereço do contrato do token para analisar.\n\n"
        "Exemplos: um endereço EVM começando com 0x, ou um endereço Solana base58."
    ),
    "scan_invalid_address": "❌ Endereço inválido. {reason}",
    "scan_unavailable": "⚠️ Alguns dados de mercado estão indisponíveis. Tente novamente.",
    "scan_limit_free_reached": (
        "⚠️ <b>Você atingiu seu limite mensal</b>\n\n"
        "Você usou <b>{used}/{limit}</b> escaneamentos gratuitos este mês.\n\n"
        "Faça upgrade para continuar:\n"
        "⭐ <b>Pro</b> — 50 escaneamentos/dia por ~$5/mês\n"
        "👑 <b>Premium</b> — Escaneamentos ilimitados por ~$15/mês\n\n"
        "Use /subscribe para ver todos os planos."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>Limite diário atingido</b>\n\n"
        "Você usou <b>{used}/{limit}</b> escaneamentos hoje.\n\n"
        "Volte amanhã, ou faça upgrade para Premium.\n\n"
        "Use /subscribe para ver todos os planos."
    ),

    # Scan report
    "report_reasons": "📋 <b>Razões</b>",
    "report_market_data": "📊 <b>Dados de mercado</b>",
    "report_price": "💵 <b>Preço:</b> {value}",
    "report_liquidity": "💧 <b>Liquidez:</b> {value} $",
    "report_volume": "📈 <b>Volume 24h:</b> {value} $",
    "report_market_cap": "🏦 <b>Cap. de mercado:</b> {value} $",
    "report_holders": "👥 <b>Detentores:</b> {value}",
    "report_chain": "⛓ <b>Rede:</b> {value}",
    "report_honeypot_yes": "🍯 <b>Honeypot:</b> SIM 🚨 NÃO NEGOCIE",
    "report_honeypot_no": "🍯 <b>Honeypot:</b> Não ✅",
    "report_taxes": "💰 <b>Taxa compra/venda:</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>Propriedade:</b> Renunciada ✅",
    "report_ownership_not_renounced": "👑 <b>Propriedade:</b> NÃO renunciada ⚠️ (dono: {owner})",
    "report_freeze_active": "🥶 <b>Autoridade de congelamento:</b> Ativa ⚠️",
    "report_freeze_disabled": "🥶 <b>Autoridade de congelamento:</b> Desativada ✅",
    "report_disclaimer": (
        "\n⚠️ <i>Ativos cripto são altamente arriscados. Sempre faça sua própria pesquisa antes de negociar.</i>"
    ),

    # Novos: supply, decimals, links
    "report_supply": "💰 <b>Oferta total:</b> {value}",
    "report_decimals": "🔢 <b>Decimais:</b> {value}",
    "report_links": "🔗 <b>Links</b>",
    "report_link_website": "🌐 Site",
    "report_link_twitter": "🐦 Twitter",
    "report_link_telegram": "📢 Telegram",
    "report_link_dexscreener": "📊 DexScreener",

    # Wallet tracking
    "wallet_menu": (
        "👛 <b>Ferramentas de carteira</b>\n\n"
        "• <code>/trackwallet &lt;endereço&gt;</code> — acompanhar uma carteira\n"
        "• <code>/mywallets</code> — ver suas carteiras\n"
        "• <code>/checkwallet &lt;endereço&gt;</code> — ver atividade recente\n"
        "• <code>/untrackwallet &lt;endereço&gt;</code> — remover uma carteira"
    ),
    "wallet_usage_track": (
        "👛 <b>Acompanhar uma carteira</b>\n\n"
        "Uso: <code>/trackwallet &lt;endereço&gt; [rede]</code>\n\n"
        "Exemplos:\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "Uso: <code>/untrackwallet &lt;endereço&gt; [rede]</code>",
    "wallet_usage_check": "Uso: <code>/checkwallet &lt;endereço&gt; [rede]</code>",
    "wallet_added": (
        "✅ <b>Carteira adicionada à sua lista.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ Rede: <b>{chain}</b>\n"
        "📊 Acompanhando: <b>{count}/{limit}</b>\n\n"
        "Você será alertado quando esta carteira se mover.\n"
        "Veja sua lista com /mywallets."
    ),
    "wallet_removed": "🗑 <code>{address}</code> removida das suas carteiras.",
    "wallet_list_empty": (
        "👛 <b>Suas carteiras acompanhadas</b>\n\n"
        "Ainda não há carteiras.\n\n"
        "Adicione uma com <code>/trackwallet &lt;endereço&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>Suas carteiras acompanhadas</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nUse /checkwallet &lt;endereço&gt; para ver atividade recente.\n"
        "Remova uma com /untrackwallet &lt;endereço&gt;."
    ),
    "wallet_check_fetching": "⏳ Buscando transações recentes…",
    "wallet_check_no_data": (
        "⚠️ Nenhuma transação recente encontrada para <code>{address}</code>\n"
        "Rede: <b>{chain}</b>\n\n"
        "Ou a carteira não tem atividade, ou o provedor está temporariamente indisponível."
    ),
    "wallet_check_header": "👛 <b>Atividade da carteira</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ Rede: <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>Fonte: Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>O rastreamento de carteiras é um recurso Pro & Premium.</b>\n\n"
        "Acompanhe carteiras do smart money e receba alertas a cada movimento.\n\n"
        "⭐ <b>Pro</b> — até 3 carteiras (~$5/mês)\n"
        "👑 <b>Premium</b> — até 20 carteiras (~$15/mês)\n\n"
        "Use /subscribe para ver todos os planos."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>Limite de carteiras atingido</b>\n\n"
        "Você está acompanhando <b>{count}/{limit}</b> carteiras.\n\n"
        "Remova uma com /untrackwallet ou faça upgrade.\n\n"
        "Use /subscribe para ver todos os planos."
    ),

    # Watchlist
    "watchlist_empty": "⭐ <b>Sua lista</b>\n\nNenhum token ainda. Use /track &lt;endereço&gt; para adicionar.",
    "watchlist_header": "⭐ <b>Sua lista</b> — {count} token(s)\n",
    "watchlist_added": "✅ <b>{symbol}</b> adicionado à sua lista.",
    "watchlist_removed": "🗑 Removido da sua lista.",
    "watchlist_limit_reached": (
        "⚠️ <b>Limite da lista atingido</b>\n\n"
        "Você está acompanhando <b>{count}/{limit}</b> tokens.\n\n"
        "Faça upgrade para adicionar mais.\n\n"
        "Use /subscribe para ver todos os planos."
    ),

    # Alerts
    "alerts_empty": (
        "🔔 <b>Alertas</b>\n\n"
        "Nenhum alerta ainda. Acompanhe um token e o CryptoPulse avisará quando:\n"
        "• o preço mudar mais de 10%\n"
        "• a liquidez mudar mais de 20%\n"
        "• o volume 24h passar de 3x a média"
    ),
    "alerts_header": "🔔 <b>Seus alertas recentes</b>\n",

    # Market / prices
    "market_header": "📊 <b>Visão do mercado</b>\n\n",
    "market_total_cap": "Cap. total do mercado: {value}",
    "market_btc_dominance": "Dominância BTC: {value}",
    "prices_header": "💹 <b>Top 10 criptomoedas</b>",
    "prices_subheader": "<i>Por capitalização de mercado (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ Não foi possível buscar os preços. Tente em um minuto.",

    # Subscription
    "subscribe_title": "💎 <b>Planos CryptoPulse</b>\n",
    "mysubscription_title": "👤 <b>Sua assinatura</b>\n\n",
    "mysubscription_plan": "Plano: <b>{plan}</b>",
    "mysubscription_price": "Preço: {price}",
    "mysubscription_expires": "⏰ Expira em: <b>{date}</b>",
    "mysubscription_limits": "\n<b>Limites atuais:</b>",
    "mysubscription_use": "\nUse /subscribe para ver opções de upgrade.",

    # Help
    "help_title": "❓ <b>Ajuda CryptoPulse</b>\n",
    "help_section_analysis": "<b>🔍 Análise de tokens</b>",
    "help_section_market": "<b>📊 Mercado &amp; dados</b>",
    "help_section_sub": "<b>💎 Assinatura</b>",
    "help_section_other": "<b>❓ Outros</b>",
    "help_supported_chains": "<b>Redes suportadas</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>Ativos cripto são altamente arriscados. Esta ferramenta fornece dados "
        "e indicadores de risco apenas para fins informativos e não constitui "
        "conselho financeiro.</i>"
    ),

    # Generic
    "feature_coming_soon": "Este recurso chegará em breve.",
    "data_unavailable": "Dados indisponíveis.",
    "not_financial_advice": "⚠️ Não é conselho financeiro.",
    "unknown_plan": "Plano desconhecido.",
    "error_generic": "⚠️ Algo deu errado. Tente novamente.",

    # Payment
    "payment_success": (
        "🎉 <b>Bem-vindo ao CryptoPulse {plan}!</b>\n\n"
        "Sua assinatura está ativa.\n"
        "⏰ Expira em: <b>{date}</b>\n"
        "⭐ Estrelas pagas: {stars}\n\n"
        "Use /mysubscription para ver seu plano."
    ),
    "payment_unknown_plan": (
        "✅ Pagamento recebido, mas o plano não pôde ser identificado. "
        "Entre em contato com o suporte com seu ID de pagamento."
    ),
    "payment_activation_failed": (
        "✅ Pagamento recebido mas a ativação falhou. "
        "Entre em contato com o suporte com seu ID de transação."
    ),
    "payment_cancel": "⚠️ Não foi possível iniciar o pagamento. Tente em um momento.",
}

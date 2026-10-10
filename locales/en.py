"""English strings for CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Welcome / menu
    "welcome": (
        "👋 <b>Welcome to CryptoPulse</b>\n\n"
        "Scan crypto tokens, track risk indicators, and receive market alerts.\n\n"
        "Choose an option below."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nChoose an option below.",
    "choose_language": "🌍 <b>Please choose your language:</b>",
    "language_set": "✅ Language set to <b>English</b>.",

    # Main menu buttons
    "btn_scan": "🔍 Scan Token",
    "btn_wallet": "👛 Analyze Wallet",
    "btn_market": "📊 Market",
    "btn_trending": "🔥 Trending",
    "btn_whales": "🐋 Whales",
    "btn_alerts": "🔔 Alerts",
    "btn_watchlist": "⭐ Watchlist",
    "btn_news": "📰 News",
    "btn_premium": "💎 Premium",
    "btn_settings": "⚙️ Settings",
    "btn_help": "❓ Help",
    "btn_back": "⬅️ Back",
    "btn_refresh": "🔄 Refresh",
    "btn_track": "⭐ Track",
    "btn_tracked": "⭐ Tracked",
    "btn_set_alert": "🔔 Set Alert",

    # Scan
    "scan_prompt": (
        "🔍 Send me the token contract address you want to scan.\n\n"
        "Examples: an EVM address starting with 0x, or a Solana base58 address."
    ),
    "scan_invalid_address": "❌ Invalid address. {reason}",
    "scan_unavailable": "⚠️ Some market data is temporarily unavailable. Please try again.",
    "scan_limit_free_reached": (
        "⚠️ <b>You've reached your monthly limit</b>\n\n"
        "You've used <b>{used}/{limit}</b> free scans this month.\n\n"
        "Upgrade to keep scanning:\n"
        "⭐ <b>Pro</b> — 50 scans/day for ~$5/month\n"
        "👑 <b>Premium</b> — Unlimited scans for ~$15/month\n\n"
        "Use /subscribe to see all plans."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>Daily limit reached</b>\n\n"
        "You've used <b>{used}/{limit}</b> scans today.\n\n"
        "Come back tomorrow, or upgrade to Premium for unlimited scans.\n\n"
        "Use /subscribe to see all plans."
    ),

    # Scan report
    "report_reasons": "📋 <b>Reasons</b>",
    "report_market_data": "📊 <b>Market Data</b>",
    "report_price": "💵 <b>Price:</b> {value}",
    "report_liquidity": "💧 <b>Liquidity:</b> ${value}",
    "report_volume": "📈 <b>Volume 24h:</b> ${value}",
    "report_market_cap": "🏦 <b>Market Cap:</b> ${value}",
    "report_holders": "👥 <b>Holders:</b> {value}",
    "report_chain": "⛓ <b>Chain:</b> {value}",
    "report_honeypot_yes": "🍯 <b>Honeypot:</b> YES 🚨 DO NOT TRADE",
    "report_honeypot_no": "🍯 <b>Honeypot:</b> No ✅",
    "report_taxes": "💰 <b>Buy/Sell tax:</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>Ownership:</b> Renounced ✅",
    "report_ownership_not_renounced": "👑 <b>Ownership:</b> NOT renounced ⚠️ (owner: {owner})",
    "report_freeze_active": "🥶 <b>Freeze Authority:</b> Active ⚠️",
    "report_freeze_disabled": "🥶 <b>Freeze Authority:</b> Disabled ✅",
    "report_disclaimer": (
        "\n⚠️ <i>Crypto assets are highly risky. Always do your own research before trading.</i>"
    ),

    # New: supply, decimals, links
    "report_supply": "💰 <b>Total Supply:</b> {value}",
    "report_decimals": "🔢 <b>Decimals:</b> {value}",
    "report_links": "🔗 <b>Links</b>",
    "report_link_website": "🌐 Website",
    "report_link_twitter": "🐦 Twitter",
    "report_link_telegram": "📢 Telegram",
    "report_link_dexscreener": "📊 DexScreener",

    # Wallet tracking
    "wallet_menu": (
        "👛 <b>Wallet tools</b>\n\n"
        "• <code>/trackwallet &lt;address&gt;</code> — track a wallet\n"
        "• <code>/mywallets</code> — see your tracked wallets\n"
        "• <code>/checkwallet &lt;address&gt;</code> — view recent activity\n"
        "• <code>/untrackwallet &lt;address&gt;</code> — remove a wallet"
    ),
    "wallet_usage_track": (
        "👛 <b>Track a wallet</b>\n\n"
        "Usage: <code>/trackwallet &lt;address&gt; [chain]</code>\n\n"
        "Examples:\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "Usage: <code>/untrackwallet &lt;address&gt; [chain]</code>",
    "wallet_usage_check": "Usage: <code>/checkwallet &lt;address&gt; [chain]</code>",
    "wallet_added": (
        "✅ <b>Wallet added to your tracking list.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ Chain: <b>{chain}</b>\n"
        "📊 Tracked: <b>{count}/{limit}</b>\n\n"
        "You'll be alerted when this wallet makes a move.\n"
        "See your list with /mywallets."
    ),
    "wallet_removed": "🗑 Removed <code>{address}</code> from your tracked wallets.",
    "wallet_list_empty": (
        "👛 <b>Your tracked wallets</b>\n\n"
        "No wallets yet.\n\n"
        "Add one with <code>/trackwallet &lt;address&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>Your tracked wallets</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nUse /checkwallet &lt;address&gt; to see recent activity.\n"
        "Remove one with /untrackwallet &lt;address&gt;."
    ),
    "wallet_check_fetching": "⏳ Fetching recent transactions…",
    "wallet_check_no_data": (
        "⚠️ No recent transactions found for <code>{address}</code>\n"
        "Chain: <b>{chain}</b>\n\n"
        "Either the wallet has no activity, or the data provider is temporarily unavailable."
    ),
    "wallet_check_header": "👛 <b>Wallet activity</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ Chain: <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>Data source: Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>Wallet tracking is a Pro & Premium feature.</b>\n\n"
        "Track smart money wallets and get alerts when they make a move.\n\n"
        "⭐ <b>Pro</b> — track up to 3 wallets (~$5/month)\n"
        "👑 <b>Premium</b> — track up to 20 wallets (~$15/month)\n\n"
        "Use /subscribe to see all plans."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>Wallet tracking limit reached</b>\n\n"
        "You're tracking <b>{count}/{limit}</b> wallets.\n\n"
        "Remove one with /untrackwallet or upgrade your plan.\n\n"
        "Use /subscribe to see all plans."
    ),

    # Watchlist
    "watchlist_empty": "⭐ <b>Your Watchlist</b>\n\nNo tokens yet. Use /track &lt;address&gt; to add one.",
    "watchlist_header": "⭐ <b>Your Watchlist</b> — {count} token(s)\n",
    "watchlist_added": "✅ Added <b>{symbol}</b> to your watchlist.",
    "watchlist_removed": "🗑 Removed from your watchlist.",
    "watchlist_limit_reached": (
        "⚠️ <b>Watchlist limit reached</b>\n\n"
        "You're tracking <b>{count}/{limit}</b> tokens.\n\n"
        "Upgrade to add more tokens.\n\n"
        "Use /subscribe to see all plans."
    ),

    # Alerts
    "alerts_empty": (
        "🔔 <b>Alerts</b>\n\n"
        "No alerts yet. Track a token and CryptoPulse will alert you when:\n"
        "• price changes by more than 10%\n"
        "• liquidity changes by more than 20%\n"
        "• 24h volume exceeds 3x the stored average"
    ),
    "alerts_header": "🔔 <b>Your recent alerts</b>\n",

    # Market / prices
    "market_header": "📊 <b>Market Overview</b>\n\n",
    "market_total_cap": "Total market cap: {value}",
    "market_btc_dominance": "BTC dominance: {value}",
    "prices_header": "💹 <b>Top 10 Cryptocurrencies</b>",
    "prices_subheader": "<i>By market capitalization (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ Could not fetch top prices right now. Please try again in a minute.",

    # Subscription
    "subscribe_title": "💎 <b>CryptoPulse Plans</b>\n",
    "mysubscription_title": "👤 <b>Your Subscription</b>\n\n",
    "mysubscription_plan": "Plan: <b>{plan}</b>",
    "mysubscription_price": "Price: {price}",
    "mysubscription_expires": "⏰ Expires on: <b>{date}</b>",
    "mysubscription_limits": "\n<b>Current limits:</b>",
    "mysubscription_use": "\nUse /subscribe to see upgrade options.",

    # Help
    "help_title": "❓ <b>CryptoPulse Help</b>\n",
    "help_section_analysis": "<b>🔍 Token Analysis</b>",
    "help_section_market": "<b>📊 Market &amp; Data</b>",
    "help_section_sub": "<b>💎 Subscription</b>",
    "help_section_other": "<b>❓ Other</b>",
    "help_supported_chains": "<b>Supported chains</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>Crypto assets are highly risky. This tool provides data "
        "and risk indicators for informational purposes only and does not "
        "constitute financial advice.</i>"
    ),

    # Generic
    "feature_coming_soon": "This feature is coming soon.",
    "data_unavailable": "Data unavailable.",
    "not_financial_advice": "⚠️ Not financial advice.",
    "unknown_plan": "Unknown plan.",
    "error_generic": "⚠️ Something went wrong. Please try again.",

    # Payment
    "payment_success": (
        "🎉 <b>Welcome to CryptoPulse {plan}!</b>\n\n"
        "Your subscription is now active.\n"
        "⏰ Expires on: <b>{date}</b>\n"
        "⭐ Stars paid: {stars}\n\n"
        "Use /mysubscription to see your plan."
    ),
    "payment_unknown_plan": (
        "✅ Payment received, but the plan could not be identified. "
        "Please contact support with your payment ID."
    ),
    "payment_activation_failed": (
        "✅ Payment received but activation failed. "
        "Please contact support with your transaction ID."
    ),
    "payment_cancel": "⚠️ Could not start payment. Please try again in a moment.",
}

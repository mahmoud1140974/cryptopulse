"""Chaînes françaises pour CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Accueil / menu
    "welcome": (
        "👋 <b>Bienvenue sur CryptoPulse</b>\n\n"
        "Analysez les tokens crypto, suivez les indicateurs de risque et recevez des alertes marché.\n\n"
        "Choisissez une option ci-dessous."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nChoisissez une option ci-dessous.",
    "choose_language": "🌍 <b>Veuillez choisir votre langue :</b>",
    "language_set": "✅ Langue définie sur <b>Français</b>.",

    # Boutons du menu principal
    "btn_scan": "🔍 Scanner un token",
    "btn_wallet": "👛 Analyser un wallet",
    "btn_market": "📊 Marché",
    "btn_trending": "🔥 Tendances",
    "btn_whales": "🐋 Baleines",
    "btn_alerts": "🔔 Alertes",
    "btn_watchlist": "⭐ Watchlist",
    "btn_news": "📰 Actualités",
    "btn_premium": "💎 Premium",
    "btn_settings": "⚙️ Paramètres",
    "btn_help": "❓ Aide",
    "btn_back": "⬅️ Retour",
    "btn_refresh": "🔄 Rafraîchir",
    "btn_track": "⭐ Suivre",
    "btn_tracked": "⭐ Suivi",
    "btn_set_alert": "🔔 Créer une alerte",

    # Scan
    "scan_prompt": (
        "🔍 Envoyez-moi l'adresse du contrat du token à analyser.\n\n"
        "Exemples : une adresse EVM commençant par 0x, ou une adresse Solana base58."
    ),
    "scan_invalid_address": "❌ Adresse invalide. {reason}",
    "scan_unavailable": "⚠️ Certaines données du marché sont temporairement indisponibles. Réessayez.",
    "scan_limit_free_reached": (
        "⚠️ <b>Vous avez atteint votre limite mensuelle</b>\n\n"
        "Vous avez utilisé <b>{used}/{limit}</b> scans gratuits ce mois-ci.\n\n"
        "Passez à un plan supérieur pour continuer :\n"
        "⭐ <b>Pro</b> — 50 scans/jour pour ~5 $/mois\n"
        "👑 <b>Premium</b> — Scans illimités pour ~15 $/mois\n\n"
        "Utilisez /subscribe pour voir tous les plans."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>Limite journalière atteinte</b>\n\n"
        "Vous avez utilisé <b>{used}/{limit}</b> scans aujourd'hui.\n\n"
        "Revenez demain, ou passez à Premium pour des scans illimités.\n\n"
        "Utilisez /subscribe pour voir tous les plans."
    ),

    # Rapport de scan
    "report_reasons": "📋 <b>Raisons</b>",
    "report_market_data": "📊 <b>Données de marché</b>",
    "report_price": "💵 <b>Prix :</b> {value}",
    "report_liquidity": "💧 <b>Liquidité :</b> {value} $",
    "report_volume": "📈 <b>Volume 24h :</b> {value} $",
    "report_market_cap": "🏦 <b>Capitalisation :</b> {value} $",
    "report_holders": "👥 <b>Détenteurs :</b> {value}",
    "report_chain": "⛓ <b>Chaîne :</b> {value}",
    "report_supply": "🪙 <b>Offre :</b> {value}",
    "report_decimals": "🔢 <b>Décimales :</b> {value}",
    "report_links": "🔗 <b>Liens</b>",
    "report_link_website": "🌐 Site web",
    "report_link_twitter": "🐦 Twitter",
    "report_link_telegram": "✈️ Telegram",
    "report_link_dexscreener": "📊 DexScreener",
    "report_honeypot_yes": "🍯 <b>Honeypot :</b> OUI 🚨 NE PAS TRADER",
    "report_honeypot_no": "🍯 <b>Honeypot :</b> Non ✅",
    "report_taxes": "💰 <b>Taxes achat/vente :</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>Propriété :</b> Renoncée ✅",
    "report_ownership_not_renounced": "👑 <b>Propriété :</b> NON renoncée ⚠️ (propriétaire : {owner})",
    "report_freeze_active": "🥶 <b>Autorité de gel :</b> Active ⚠️",
    "report_freeze_disabled": "🥶 <b>Autorité de gel :</b> Désactivée ✅",
    "report_disclaimer": (
        "\n⚠️ <i>Les actifs crypto sont très risqués. Faites toujours vos propres recherches avant de trader.</i>"
    ),

    # Raisons du rapport de risque
    "reason_insufficient_data": "Données insuffisantes pour évaluer le risque",
    "reason_no_risk_flags": "Aucun signal de risque trouvé dans les données disponibles",
    "reason_liquidity_very_low": "Liquidité très faible ({value})",
    "reason_liquidity_low": "Liquidité faible ({value})",
    "reason_liquidity_modest": "Liquidité modeste ({value})",
    "reason_volume_very_low": "Volume 24h très faible ({value})",
    "reason_volume_low": "Volume 24h faible ({value})",
    "reason_mcap_very_small": "Capitalisation très petite ({value})",
    "reason_mcap_small": "Capitalisation petite ({value})",
    "reason_age_less_than_day": "Token créé il y a moins d'un jour",
    "reason_age_days": "Token créé il y a {days} jour(s)",
    "reason_age_young": "Token jeune ({days} jour(s))",
    "reason_top10_control": "Les 10 plus gros détenteurs contrôlent {pct} % de l'offre",
    "reason_contract_unverified": "Le code source du contrat n'est pas vérifié",
    "reason_ownership_not_renounced": "La propriété du contrat n'a pas été abandonnée",
    "reason_mint_function": "Fonction de mint détectée dans le contrat",
    "reason_blacklist_function": "Fonction de blacklist détectée dans le contrat",
    "reason_honeypot_detected": "Honeypot détecté",
    "reason_proxy_contract": "Contrat proxy ou upgradable détecté",
    "reason_freeze_authority": "Autorité de gel Solana active",
    "reason_high_tax_buy": "Taxe d'achat élevée détectée ({value})",
    "reason_high_tax_sell": "Taxe de vente élevée détectée ({value})",
    "reason_high_tax_both": "Taxes d'achat et de vente élevées détectées (achat {buy}, vente {sell})",
    "reason_one_category": "Une seule catégorie de données disponible ; le risque est peut-être sous-estimé",
    "reason_no_security_data": "Aucune donnée de sécurité disponible ; le risque est peut-être sous-estimé",
    "reason_no_holder_data": "Aucune donnée de concentration des détenteurs disponible",
    "reason_no_market_data": "Aucune donnée de marché disponible",
    "reason_unknown_fields": "Inconnu : {fields}",

    # Suivi de wallet
    "wallet_menu": (
        "👛 <b>Outils wallet</b>\n\n"
        "• <code>/trackwallet &lt;adresse&gt;</code> — suivre un wallet\n"
        "• <code>/mywallets</code> — voir vos wallets suivis\n"
        "• <code>/checkwallet &lt;adresse&gt;</code> — voir l'activité récente\n"
        "• <code>/untrackwallet &lt;adresse&gt;</code> — retirer un wallet"
    ),
    "wallet_usage_track": (
        "👛 <b>Suivre un wallet</b>\n\n"
        "Usage : <code>/trackwallet &lt;adresse&gt; [chaîne]</code>\n\n"
        "Exemples :\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "Usage : <code>/untrackwallet &lt;adresse&gt; [chaîne]</code>",
    "wallet_usage_check": "Usage : <code>/checkwallet &lt;adresse&gt; [chaîne]</code>",
    "wallet_added": (
        "✅ <b>Wallet ajouté à votre liste de suivi.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ Chaîne : <b>{chain}</b>\n"
        "📊 Suivis : <b>{count}/{limit}</b>\n\n"
        "Vous serez alerté quand ce wallet effectue un mouvement.\n"
        "Voir votre liste avec /mywallets."
    ),
    "wallet_removed": "🗑 <code>{address}</code> retiré de vos wallets suivis.",
    "wallet_list_empty": (
        "👛 <b>Vos wallets suivis</b>\n\n"
        "Aucun wallet pour le moment.\n\n"
        "Ajoutez-en un avec <code>/trackwallet &lt;adresse&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>Vos wallets suivis</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nUtilisez /checkwallet &lt;adresse&gt; pour voir l'activité récente.\n"
        "Retirez-en un avec /untrackwallet &lt;adresse&gt;."
    ),
    "wallet_check_fetching": "⏳ Récupération des transactions récentes…",
    "wallet_check_no_data": (
        "⚠️ Aucune transaction récente trouvée pour <code>{address}</code>\n"
        "Chaîne : <b>{chain}</b>\n\n"
        "Soit le wallet est inactif, soit le fournisseur de données est temporairement indisponible."
    ),
    "wallet_check_header": "👛 <b>Activité du wallet</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ Chaîne : <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>Source : Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>Le suivi de wallet est une fonctionnalité Pro & Premium.</b>\n\n"
        "Suivez les wallets du smart money et recevez des alertes à chaque mouvement.\n\n"
        "⭐ <b>Pro</b> — jusqu'à 3 wallets (~5 $/mois)\n"
        "👑 <b>Premium</b> — jusqu'à 20 wallets (~15 $/mois)\n\n"
        "Utilisez /subscribe pour voir tous les plans."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>Limite de suivi de wallets atteinte</b>\n\n"
        "Vous suivez <b>{count}/{limit}</b> wallets.\n\n"
        "Retirez-en un avec /untrackwallet ou passez à un plan supérieur.\n\n"
        "Utilisez /subscribe pour voir tous les plans."
    ),

    # Watchlist
    "watchlist_empty": "⭐ <b>Votre Watchlist</b>\n\nAucun token pour le moment. Utilisez /track &lt;adresse&gt; pour en ajouter un.",
    "watchlist_header": "⭐ <b>Votre Watchlist</b> — {count} token(s)\n",
    "watchlist_added": "✅ <b>{symbol}</b> ajouté à votre watchlist.",
    "watchlist_removed": "🗑 Retiré de votre watchlist.",
    "watchlist_limit_reached": (
        "⚠️ <b>Limite de watchlist atteinte</b>\n\n"
        "Vous suivez <b>{count}/{limit}</b> tokens.\n\n"
        "Passez à un plan supérieur pour en ajouter plus.\n\n"
        "Utilisez /subscribe pour voir tous les plans."
    ),

    # Alertes
    "alerts_empty": (
        "🔔 <b>Alertes</b>\n\n"
        "Aucune alerte pour le moment. Suivez un token et CryptoPulse vous alertera quand :\n"
        "• le prix change de plus de 10 %\n"
        "• la liquidité change de plus de 20 %\n"
        "• le volume 24h dépasse 3x la moyenne enregistrée"
    ),
    "alerts_header": "🔔 <b>Vos alertes récentes</b>\n",

    # Marché / prix
    "market_header": "📊 <b>Aperçu du marché</b>\n\n",
    "market_total_cap": "Cap. totale du marché : {value}",
    "market_btc_dominance": "Domination BTC : {value}",
    "prices_header": "💹 <b>Top 10 cryptomonnaies</b>",
    "prices_subheader": "<i>Par capitalisation boursière (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ Impossible de récupérer les prix pour le moment. Réessayez dans une minute.",

    # Abonnement
    "subscribe_title": "💎 <b>Plans CryptoPulse</b>\n",
    "mysubscription_title": "👤 <b>Votre abonnement</b>\n\n",
    "mysubscription_plan": "Plan : <b>{plan}</b>",
    "mysubscription_price": "Prix : {price}",
    "mysubscription_expires": "⏰ Expire le : <b>{date}</b>",
    "mysubscription_limits": "\n<b>Limites actuelles :</b>",
    "mysubscription_use": "\nUtilisez /subscribe pour voir les options de mise à niveau.",

    # Aide
    "help_title": "❓ <b>Aide CryptoPulse</b>\n",
    "help_section_analysis": "<b>🔍 Analyse de token</b>",
    "help_section_market": "<b>📊 Marché &amp; données</b>",
    "help_section_sub": "<b>💎 Abonnement</b>",
    "help_section_other": "<b>❓ Autre</b>",
    "help_supported_chains": "<b>Chaînes supportées</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>Les actifs crypto sont très risqués. Cet outil fournit des données "
        "et indicateurs de risque à titre informatif uniquement et ne constitue pas "
        "un conseil financier.</i>"
    ),

    # Générique
    "feature_coming_soon": "Cette fonctionnalité arrive bientôt.",
    "data_unavailable": "Données indisponibles.",
    "not_financial_advice": "⚠️ Pas un conseil financier.",
    "unknown_plan": "Plan inconnu.",
    "error_generic": "⚠️ Une erreur est survenue. Réessayez.",

    # Paiement
    "payment_success": (
        "🎉 <b>Bienvenue dans CryptoPulse {plan} !</b>\n\n"
        "Votre abonnement est maintenant actif.\n"
        "⏰ Expire le : <b>{date}</b>\n"
        "⭐ Étoiles payées : {stars}\n\n"
        "Utilisez /mysubscription pour voir votre plan."
    ),
    "payment_unknown_plan": (
        "✅ Paiement reçu, mais le plan n'a pas pu être identifié. "
        "Contactez le support avec votre ID de paiement."
    ),
    "payment_activation_failed": (
        "✅ Paiement reçu mais l'activation a échoué. "
        "Contactez le support avec votre ID de transaction."
    ),
    "payment_cancel": "⚠️ Impossible de démarrer le paiement. Réessayez dans un instant.",
}

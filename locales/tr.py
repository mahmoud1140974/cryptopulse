"""Turkish strings for CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Karşılama / menü
    "welcome": (
        "👋 <b>CryptoPulse'a hoş geldiniz</b>\n\n"
        "Kripto tokenları tarayın, risk göstergelerini takip edin ve piyasa uyarıları alın.\n\n"
        "Aşağıdan bir seçenek seçin."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nAşağıdan bir seçenek seçin.",
    "choose_language": "🌍 <b>Lütfen dilinizi seçin:</b>",
    "language_set": "✅ Dil <b>Türkçe</b> olarak ayarlandı.",

    # Ana menü butonları
    "btn_scan": "🔍 Token Tara",
    "btn_wallet": "👛 Cüzdan Analiz",
    "btn_market": "📊 Piyasa",
    "btn_trending": "🔥 Trendler",
    "btn_whales": "🐋 Balinalar",
    "btn_alerts": "🔔 Uyarılar",
    "btn_watchlist": "⭐ İzleme Listesi",
    "btn_news": "📰 Haberler",
    "btn_premium": "💎 Premium",
    "btn_settings": "⚙️ Ayarlar",
    "btn_help": "❓ Yardım",
    "btn_back": "⬅️ Geri",
    "btn_refresh": "🔄 Yenile",
    "btn_track": "⭐ Takip Et",
    "btn_tracked": "⭐ Takipte",
    "btn_set_alert": "🔔 Uyarı Kur",

    # Tarama
    "scan_prompt": (
        "🔍 Taramak istediğiniz token sözleşme adresini gönderin.\n\n"
        "Örnekler: 0x ile başlayan EVM adresi veya Solana base58 adresi."
    ),
    "scan_invalid_address": "❌ Geçersiz adres. {reason}",
    "scan_unavailable": "⚠️ Bazı piyasa verileri geçici olarak kullanılamıyor. Tekrar deneyin.",
    "scan_limit_free_reached": (
        "⚠️ <b>Aylık limitinize ulaştınız</b>\n\n"
        "Bu ay <b>{used}/{limit}</b> ücretsiz tarama kullandınız.\n\n"
        "Devam etmek için yükseltin:\n"
        "⭐ <b>Pro</b> — günde 50 tarama (~5$/ay)\n"
        "👑 <b>Premium</b> — Sınırsız tarama (~15$/ay)\n\n"
        "Tüm planlar için /subscribe."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>Günlük limite ulaşıldı</b>\n\n"
        "Bugün <b>{used}/{limit}</b> tarama kullandınız.\n\n"
        "Yarın geri dönün veya Premium'a yükseltin.\n\n"
        "Tüm planlar için /subscribe."
    ),

    # Tarama raporu
    "report_reasons": "📋 <b>Nedenler</b>",
    "report_market_data": "📊 <b>Piyasa Verileri</b>",
    "report_price": "💵 <b>Fiyat:</b> {value}",
    "report_liquidity": "💧 <b>Likidite:</b> {value} $",
    "report_volume": "📈 <b>24s Hacim:</b> {value} $",
    "report_market_cap": "🏦 <b>Piyasa Değeri:</b> {value} $",
    "report_holders": "👥 <b>Sahipler:</b> {value}",
    "report_chain": "⛓ <b>Ağ:</b> {value}",
    "report_honeypot_yes": "🍯 <b>Honeypot:</b> EVET 🚨 ALIM SATIM YAPMAYIN",
    "report_honeypot_no": "🍯 <b>Honeypot:</b> Hayır ✅",
    "report_taxes": "💰 <b>Alım/Satım vergisi:</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>Sahiplik:</b> Feragat edildi ✅",
    "report_ownership_not_renounced": "👑 <b>Sahiplik:</b> Feragat EDİLMEDİ ⚠️ (sahip: {owner})",
    "report_freeze_active": "🥶 <b>Dondurma Yetkisi:</b> Aktif ⚠️",
    "report_freeze_disabled": "🥶 <b>Dondurma Yetkisi:</b> Devre dışı ✅",
    "report_disclaimer": (
        "\n⚠️ <i>Kripto varlıklar yüksek risklidir. İşlem yapmadan önce mutlaka kendi araştırmanızı yapın.</i>"
    ),

    # Cüzdan takibi
    "wallet_menu": (
        "👛 <b>Cüzdan araçları</b>\n\n"
        "• <code>/trackwallet &lt;adres&gt;</code> — cüzdanı takip et\n"
        "• <code>/mywallets</code> — takip edilen cüzdanlar\n"
        "• <code>/checkwallet &lt;adres&gt;</code> — son hareketler\n"
        "• <code>/untrackwallet &lt;adres&gt;</code> — cüzdanı kaldır"
    ),
    "wallet_usage_track": (
        "👛 <b>Cüzdan takip et</b>\n\n"
        "Kullanım: <code>/trackwallet &lt;adres&gt; [ağ]</code>\n\n"
        "Örnekler:\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "Kullanım: <code>/untrackwallet &lt;adres&gt; [ağ]</code>",
    "wallet_usage_check": "Kullanım: <code>/checkwallet &lt;adres&gt; [ağ]</code>",
    "wallet_added": (
        "✅ <b>Cüzdan takip listenize eklendi.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ Ağ: <b>{chain}</b>\n"
        "📊 Takipte: <b>{count}/{limit}</b>\n\n"
        "Bu cüzdan hareket ettiğinde bilgilendirileceksiniz.\n"
        "Listeyi görüntüle: /mywallets."
    ),
    "wallet_removed": "🗑 <code>{address}</code> takipten çıkarıldı.",
    "wallet_list_empty": (
        "👛 <b>Takip edilen cüzdanlar</b>\n\n"
        "Henüz cüzdan yok.\n\n"
        "Eklemek için: <code>/trackwallet &lt;adres&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>Takip edilen cüzdanlar</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nSon hareketler için /checkwallet &lt;adres&gt;.\n"
        "Kaldırmak için /untrackwallet &lt;adres&gt;."
    ),
    "wallet_check_fetching": "⏳ Son işlemler alınıyor…",
    "wallet_check_no_data": (
        "⚠️ <code>{address}</code> için son işlem bulunamadı\n"
        "Ağ: <b>{chain}</b>\n\n"
        "Ya cüzdan aktif değil ya da sağlayıcı geçici olarak kullanılamıyor."
    ),
    "wallet_check_header": "👛 <b>Cüzdan hareketleri</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ Ağ: <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>Kaynak: Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>Cüzdan takibi Pro ve Premium özelliğidir.</b>\n\n"
        "Akıllı para cüzdanlarını takip edin ve hareketlerinde uyarı alın.\n\n"
        "⭐ <b>Pro</b> — 3 cüzdana kadar (~5$/ay)\n"
        "👑 <b>Premium</b> — 20 cüzdana kadar (~15$/ay)\n\n"
        "Tüm planlar için /subscribe."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>Cüzdan takip limitine ulaşıldı</b>\n\n"
        "<b>{count}/{limit}</b> cüzdan takip ediyorsunuz.\n\n"
        "/untrackwallet ile kaldırın veya planı yükseltin.\n\n"
        "Tüm planlar için /subscribe."
    ),

    # İzleme listesi
    "watchlist_empty": "⭐ <b>İzleme Listeniz</b>\n\nHenüz token yok. Eklemek için /track &lt;adres&gt;.",
    "watchlist_header": "⭐ <b>İzleme Listeniz</b> — {count} token\n",
    "watchlist_added": "✅ <b>{symbol}</b> izleme listenize eklendi.",
    "watchlist_removed": "🗑 Listenizden kaldırıldı.",
    "watchlist_limit_reached": (
        "⚠️ <b>İzleme listesi limitine ulaşıldı</b>\n\n"
        "<b>{count}/{limit}</b> token takip ediyorsunuz.\n\n"
        "Daha fazla eklemek için yükseltin.\n\n"
        "Tüm planlar için /subscribe."
    ),

    # Uyarılar
    "alerts_empty": (
        "🔔 <b>Uyarılar</b>\n\n"
        "Henüz uyarı yok. Bir token takip edin, CryptoPulse şu durumlarda uyarır:\n"
        "• fiyat %10'dan fazla değişirse\n"
        "• likidite %20'den fazla değişirse\n"
        "• 24s hacim ortalamanın 3 katını geçerse"
    ),
    "alerts_header": "🔔 <b>Son uyarılarınız</b>\n",

    # Piyasa / fiyatlar
    "market_header": "📊 <b>Piyasa Genel Bakış</b>\n\n",
    "market_total_cap": "Toplam piyasa değeri: {value}",
    "market_btc_dominance": "BTC hakimiyeti: {value}",
    "prices_header": "💹 <b>En İyi 10 Kripto</b>",
    "prices_subheader": "<i>Piyasa değerine göre (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ Fiyatlar alınamadı. Bir dakika sonra tekrar deneyin.",

    # Abonelik
    "subscribe_title": "💎 <b>CryptoPulse Planları</b>\n",
    "mysubscription_title": "👤 <b>Aboneliğiniz</b>\n\n",
    "mysubscription_plan": "Plan: <b>{plan}</b>",
    "mysubscription_price": "Fiyat: {price}",
    "mysubscription_expires": "⏰ Bitiş: <b>{date}</b>",
    "mysubscription_limits": "\n<b>Mevcut limitler:</b>",
    "mysubscription_use": "\nYükseltme seçenekleri için /subscribe.",

    # Yardım
    "help_title": "❓ <b>CryptoPulse Yardım</b>\n",
    "help_section_analysis": "<b>🔍 Token Analizi</b>",
    "help_section_market": "<b>📊 Piyasa &amp; Veriler</b>",
    "help_section_sub": "<b>💎 Abonelik</b>",
    "help_section_other": "<b>❓ Diğer</b>",
    "help_supported_chains": "<b>Desteklenen ağlar</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>Kripto varlıklar yüksek risklidir. Bu araç yalnızca bilgilendirme "
        "amaçlı veri ve risk göstergeleri sunar, finansal tavsiye niteliği taşımaz.</i>"
    ),

    # Genel
    "feature_coming_soon": "Bu özellik yakında geliyor.",
    "data_unavailable": "Veri kullanılamıyor.",
    "not_financial_advice": "⚠️ Finansal tavsiye değildir.",
    "unknown_plan": "Bilinmeyen plan.",
    "error_generic": "⚠️ Bir şeyler ters gitti. Tekrar deneyin.",

    # Ödeme
    "payment_success": (
        "🎉 <b>CryptoPulse {plan}'a hoş geldiniz!</b>\n\n"
        "Aboneliğiniz aktif.\n"
        "⏰ Bitiş: <b>{date}</b>\n"
        "⭐ Ödenen yıldız: {stars}\n\n"
        "Planınızı görmek için /mysubscription."
    ),
    "payment_unknown_plan": (
        "✅ Ödeme alındı ancak plan tanımlanamadı. "
        "Ödeme kimliğinizle destek ile iletişime geçin."
    ),
    "payment_activation_failed": (
        "✅ Ödeme alındı ancak etkinleştirme başarısız. "
        "İşlem kimliğinizle destek ile iletişime geçin."
    ),
    "payment_cancel": "⚠️ Ödeme başlatılamadı. Bir anda tekrar deneyin.",
}

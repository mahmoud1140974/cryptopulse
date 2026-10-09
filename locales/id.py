"""Indonesian strings for CryptoPulse."""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Welcome / menu
    "welcome": (
        "👋 <b>Selamat datang di CryptoPulse</b>\n\n"
        "Pindai token kripto, pantau indikator risiko, dan terima peringatan pasar.\n\n"
        "Pilih opsi di bawah ini."
    ),
    "menu_short": "👋 <b>CryptoPulse</b>\n\nPilih opsi di bawah ini.",
    "choose_language": "🌍 <b>Silakan pilih bahasa Anda:</b>",
    "language_set": "✅ Bahasa diatur ke <b>Bahasa Indonesia</b>.",

    # Main menu buttons
    "btn_scan": "🔍 Pindai Token",
    "btn_wallet": "👛 Analisis Wallet",
    "btn_market": "📊 Pasar",
    "btn_trending": "🔥 Trending",
    "btn_whales": "🐋 Paus",
    "btn_alerts": "🔔 Peringatan",
    "btn_watchlist": "⭐ Daftar Pantau",
    "btn_news": "📰 Berita",
    "btn_premium": "💎 Premium",
    "btn_settings": "⚙️ Pengaturan",
    "btn_help": "❓ Bantuan",
    "btn_back": "⬅️ Kembali",
    "btn_refresh": "🔄 Segarkan",
    "btn_track": "⭐ Pantau",
    "btn_tracked": "⭐ Dipantau",
    "btn_set_alert": "🔔 Buat Peringatan",

    # Scan
    "scan_prompt": (
        "🔍 Kirimkan saya alamat kontrak token yang ingin dipindai.\n\n"
        "Contoh: alamat EVM yang dimulai dengan 0x, atau alamat Solana base58."
    ),
    "scan_invalid_address": "❌ Alamat tidak valid. {reason}",
    "scan_unavailable": "⚠️ Beberapa data pasar sementara tidak tersedia. Silakan coba lagi.",
    "scan_limit_free_reached": (
        "⚠️ <b>Anda telah mencapai batas bulanan</b>\n\n"
        "Anda telah menggunakan <b>{used}/{limit}</b> pemindaian gratis bulan ini.\n\n"
        "Tingkatkan untuk terus memindai:\n"
        "⭐ <b>Pro</b> — 50 pemindaian/hari sekitar $5/bulan\n"
        "👑 <b>Premium</b> — Pemindaian tak terbatas sekitar $15/bulan\n\n"
        "Gunakan /subscribe untuk melihat semua paket."
    ),
    "scan_limit_daily_reached": (
        "⚠️ <b>Batas harian tercapai</b>\n\n"
        "Anda telah menggunakan <b>{used}/{limit}</b> pemindaian hari ini.\n\n"
        "Kembali besok, atau tingkatkan ke Premium untuk pemindaian tak terbatas.\n\n"
        "Gunakan /subscribe untuk melihat semua paket."
    ),

    # Scan report
    "report_reasons": "📋 <b>Alasan</b>",
    "report_market_data": "📊 <b>Data Pasar</b>",
    "report_price": "💵 <b>Harga:</b> {value}",
    "report_liquidity": "💧 <b>Likuiditas:</b> {value} $",
    "report_volume": "📈 <b>Volume 24j:</b> {value} $",
    "report_market_cap": "🏦 <b>Kapitalisasi:</b> {value} $",
    "report_holders": "👥 <b>Pemegang:</b> {value}",
    "report_chain": "⛓ <b>Jaringan:</b> {value}",
    "report_honeypot_yes": "🍯 <b>Honeypot:</b> YA 🚨 JANGAN TRADING",
    "report_honeypot_no": "🍯 <b>Honeypot:</b> Tidak ✅",
    "report_taxes": "💰 <b>Pajak beli/jual:</b> {buy} / {sell}",
    "report_ownership_renounced": "👑 <b>Kepemilikan:</b> Dilepaskan ✅",
    "report_ownership_not_renounced": "👑 <b>Kepemilikan:</b> TIDAK dilepaskan ⚠️ (pemilik: {owner})",
    "report_freeze_active": "🥶 <b>Otoritas Pembekuan:</b> Aktif ⚠️",
    "report_freeze_disabled": "🥶 <b>Otoritas Pembekuan:</b> Nonaktif ✅",
    "report_disclaimer": (
        "\n⚠️ <i>Aset kripto sangat berisiko. Selalu lakukan riset sendiri sebelum trading.</i>"
    ),

    # Wallet tracking
    "wallet_menu": (
        "👛 <b>Alat wallet</b>\n\n"
        "• <code>/trackwallet &lt;alamat&gt;</code> — pantau wallet\n"
        "• <code>/mywallets</code> — lihat wallet yang dipantau\n"
        "• <code>/checkwallet &lt;alamat&gt;</code> — lihat aktivitas terbaru\n"
        "• <code>/untrackwallet &lt;alamat&gt;</code> — hapus wallet"
    ),
    "wallet_usage_track": (
        "👛 <b>Pantau wallet</b>\n\n"
        "Penggunaan: <code>/trackwallet &lt;alamat&gt; [jaringan]</code>\n\n"
        "Contoh:\n"
        "<code>/trackwallet 0xabc...</code>\n"
        "<code>/trackwallet DezXAZ... solana</code>"
    ),
    "wallet_usage_untrack": "Penggunaan: <code>/untrackwallet &lt;alamat&gt; [jaringan]</code>",
    "wallet_usage_check": "Penggunaan: <code>/checkwallet &lt;alamat&gt; [jaringan]</code>",
    "wallet_added": (
        "✅ <b>Wallet ditambahkan ke daftar pantauan Anda.</b>\n\n"
        "👛 <code>{address}</code>\n"
        "⛓ Jaringan: <b>{chain}</b>\n"
        "📊 Dipantau: <b>{count}/{limit}</b>\n\n"
        "Anda akan diberi tahu saat wallet ini bergerak.\n"
        "Lihat daftar dengan /mywallets."
    ),
    "wallet_removed": "🗑 <code>{address}</code> dihapus dari wallet yang dipantau.",
    "wallet_list_empty": (
        "👛 <b>Wallet yang Anda pantau</b>\n\n"
        "Belum ada wallet.\n\n"
        "Tambahkan dengan <code>/trackwallet &lt;alamat&gt;</code>"
    ),
    "wallet_list_header": "👛 <b>Wallet yang Anda pantau</b> — {count}/{limit}\n",
    "wallet_list_footer": (
        "\nGunakan /checkwallet &lt;alamat&gt; untuk melihat aktivitas terbaru.\n"
        "Hapus dengan /untrackwallet &lt;alamat&gt;."
    ),
    "wallet_check_fetching": "⏳ Mengambil transaksi terbaru…",
    "wallet_check_no_data": (
        "⚠️ Tidak ditemukan transaksi terbaru untuk <code>{address}</code>\n"
        "Jaringan: <b>{chain}</b>\n\n"
        "Wallet tidak aktif, atau penyedia data sementara tidak tersedia."
    ),
    "wallet_check_header": "👛 <b>Aktivitas wallet</b> — <code>{address}</code>",
    "wallet_check_chain": "⛓ Jaringan: <b>{chain}</b>\n",
    "wallet_check_source": "\n<i>Sumber data: Etherscan / Helius</i>",
    "wallet_locked": (
        "🔒 <b>Pelacakan wallet adalah fitur Pro & Premium.</b>\n\n"
        "Pantau wallet smart money dan dapatkan peringatan saat bergerak.\n\n"
        "⭐ <b>Pro</b> — hingga 3 wallet (~$5/bulan)\n"
        "👑 <b>Premium</b> — hingga 20 wallet (~15$/bulan)\n\n"
        "Gunakan /subscribe untuk melihat semua paket."
    ),
    "wallet_limit_reached": (
        "⚠️ <b>Batas pelacakan wallet tercapai</b>\n\n"
        "Anda memantau <b>{count}/{limit}</b> wallet.\n\n"
        "Hapus dengan /untrackwallet atau tingkatkan paket Anda.\n\n"
        "Gunakan /subscribe untuk melihat semua paket."
    ),

    # Watchlist
    "watchlist_empty": "⭐ <b>Daftar Pantau Anda</b>\n\nBelum ada token. Gunakan /track &lt;alamat&gt; untuk menambahkan.",
    "watchlist_header": "⭐ <b>Daftar Pantau Anda</b> — {count} token\n",
    "watchlist_added": "✅ <b>{symbol}</b> ditambahkan ke daftar pantau Anda.",
    "watchlist_removed": "🗑 Dihapus dari daftar pantau Anda.",
    "watchlist_limit_reached": (
        "⚠️ <b>Batas daftar pantau tercapai</b>\n\n"
        "Anda memantau <b>{count}/{limit}</b> token.\n\n"
        "Tingkatkan untuk menambah lebih banyak.\n\n"
        "Gunakan /subscribe untuk melihat semua paket."
    ),

    # Alerts
    "alerts_empty": (
        "🔔 <b>Peringatan</b>\n\n"
        "Belum ada peringatan. Pantau token dan CryptoPulse akan memberi tahu Anda saat:\n"
        "• harga berubah lebih dari 10%\n"
        "• likuiditas berubah lebih dari 20%\n"
        "• volume 24j melebihi 3x rata-rata tersimpan"
    ),
    "alerts_header": "🔔 <b>Peringatan terbaru Anda</b>\n",

    # Market / prices
    "market_header": "📊 <b>Ikhtisar Pasar</b>\n\n",
    "market_total_cap": "Total kapitalisasi pasar: {value}",
    "market_btc_dominance": "Dominasi BTC: {value}",
    "prices_header": "💹 <b>10 Cryptocurrency Teratas</b>",
    "prices_subheader": "<i>Berdasarkan kapitalisasi pasar (CoinGecko)</i>\n",
    "prices_unavailable": "⚠️ Tidak dapat mengambil harga saat ini. Silakan coba lagi dalam satu menit.",

    # Subscription
    "subscribe_title": "💎 <b>Paket CryptoPulse</b>\n",
    "mysubscription_title": "👤 <b>Langganan Anda</b>\n\n",
    "mysubscription_plan": "Paket: <b>{plan}</b>",
    "mysubscription_price": "Harga: {price}",
    "mysubscription_expires": "⏰ Berakhir pada: <b>{date}</b>",
    "mysubscription_limits": "\n<b>Batas saat ini:</b>",
    "mysubscription_use": "\nGunakan /subscribe untuk melihat opsi peningkatan.",

    # Help
    "help_title": "❓ <b>Bantuan CryptoPulse</b>\n",
    "help_section_analysis": "<b>🔍 Analisis Token</b>",
    "help_section_market": "<b>📊 Pasar &amp; Data</b>",
    "help_section_sub": "<b>💎 Langganan</b>",
    "help_section_other": "<b>❓ Lainnya</b>",
    "help_supported_chains": "<b>Jaringan yang didukung</b>\nEVM + Solana",
    "help_disclaimer": (
        "⚠️ <i>Aset kripto sangat berisiko. Alat ini menyediakan data "
        "dan indikator risiko untuk tujuan informasi saja dan bukan merupakan "
        "nasihat keuangan.</i>"
    ),

    # Generic
    "feature_coming_soon": "Fitur ini akan segera hadir.",
    "data_unavailable": "Data tidak tersedia.",
    "not_financial_advice": "⚠️ Bukan nasihat keuangan.",
    "unknown_plan": "Paket tidak dikenal.",
    "error_generic": "⚠️ Terjadi kesalahan. Silakan coba lagi.",

    # Payment
    "payment_success": (
        "🎉 <b>Selamat datang di CryptoPulse {plan}!</b>\n\n"
        "Langganan Anda sekarang aktif.\n"
        "⏰ Berakhir pada: <b>{date}</b>\n"
        "⭐ Bintang dibayar: {stars}\n\n"
        "Gunakan /mysubscription untuk melihat paket Anda."
    ),
    "payment_unknown_plan": (
        "✅ Pembayaran diterima, tetapi paket tidak dapat diidentifikasi. "
        "Silakan hubungi dukungan dengan ID pembayaran Anda."
    ),
    "payment_activation_failed": (
        "✅ Pembayaran diterima tetapi aktivasi gagal. "
        "Silakan hubungi dukungan dengan ID transaksi Anda."
    ),
    "payment_cancel": "⚠️ Tidak dapat memulai pembayaran. Silakan coba lagi sebentar lagi.",
}

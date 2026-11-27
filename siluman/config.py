"""Semua angka dan teks yang bisa disetel untuk crawler."""

# Pemilik: Penjelajah. Rujukan: Panduan hlm. 16-17.

# TODO 1:
UA_BROWSER = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"

# TODO 2:
UA_GOOGLEBOT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/157.0.0.0 Safari/537.36"

# TODO 3:
REFERER_GOOGLE = "https://www.google.com/"

# TODO 4:
PERSONA = {
    "browser": {"User-Agent": UA_BROWSER},
    "googlebot": {"User-Agent": UA_GOOGLEBOT},
    "dari_google": {"User-Agent": UA_BROWSER, "Referer": REFERER_GOOGLE},
}

# TODO 5:
URUTAN_PERSONA = ["dari_google", "googlebot", "browser"]

# TODO 6:
JEDA_PER_DOMAIN = 1.0
MAKS_DOMAIN_BERSAMAAN = 50
TIMEOUT_DETIK = 20
BATAS_UKURAN = 2_000_000
MAKS_LOMPATAN_REDIRECT = 5

# TODO 7:
LOKASI_DB = "data/siluman.db"
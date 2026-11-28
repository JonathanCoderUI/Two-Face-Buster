"""Semua angka dan teks yang bisa disetel untuk crawler."""

# Pemilik: Penjelajah. Rujukan: Panduan hlm. 16-17.

# Dipakai persona "browser" dan "dari_google".
UA_BROWSER = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"

# Dipakai persona "googlebot". Situs siluman mengenali Googlebot dari string ini.
UA_GOOGLEBOT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/157.0.0.0 Safari/537.36"

# Asal kunjungan palsu untuk persona "dari_google".
REFERER_GOOGLE = "https://www.google.com/"

# Header yang dikirim tiap persona.
PERSONA = {
    "browser": {"User-Agent": UA_BROWSER},
    "googlebot": {"User-Agent": UA_GOOGLEBOT},
    "dari_google": {"User-Agent": UA_BROWSER, "Referer": REFERER_GOOGLE},
}

# Urutan tiga kunjungan untuk satu URL.
URUTAN_PERSONA = ["dari_google", "googlebot", "browser"]

# Jeda antar kunjungan ke domain yang sama, dalam detik.
JEDA_PER_DOMAIN = 1.0
# Batas jumlah domain yang dikunjungi bersamaan.
MAKS_DOMAIN_BERSAMAAN = 50
# Batas total waktu satu kunjungan, dalam detik.
TIMEOUT_DETIK = 20
# Batas ukuran isi halaman yang dibaca, dalam byte.
BATAS_UKURAN = 2_000_000
# Batas redirect berurutan di situs yang sama sebelum dianggap berputar.
MAKS_LOMPATAN_REDIRECT = 5

LOKASI_DB = "data/siluman.db"

"""Semua angka dan teks yang bisa disetel untuk crawler."""

# Pemilik: Penjelajah. Rujukan: Panduan hlm. 16-17.

# TODO 1:
# User-Agent browser, salin dari chrome://version di laptopmu sendiri.
UA_BROWSER = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"

# TODO 2:
# User-Agent Googlebot dari dokumentasi crawler Google.
UA_GOOGLEBOT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/157.0.0.0 Safari/537.36"

# TODO 3:
# Referer yang dipakai persona dari_google.
REFERER_GOOGLE = "https://www.google.com/"

# TODO 4:
# Header untuk tiap persona: browser, googlebot, dari_google (browser + Referer Google).
PERSONA = ...

# TODO 5:
# Urutan kunjungan persona. dari_google dikunjungi paling awal.
URUTAN_PERSONA = ...

# TODO 6:
# Batas sopan: jeda per domain minimal 1 detik, maksimal 50 domain bersamaan,
# batas waktu, batas ukuran HTML, batas lompatan redirect di situs yang sama.
JEDA_PER_DOMAIN = ...
MAKS_DOMAIN_BERSAMAAN = ...
TIMEOUT_DETIK = ...
BATAS_UKURAN = ...
MAKS_LOMPATAN_REDIRECT = ...

# TODO 7:
# Lokasi database bersama (dipakai main.py dan dashboard.py).
LOKASI_DB = ...

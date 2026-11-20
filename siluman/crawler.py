"""Mengunjungi setiap URL sebagai tiga persona dan menyimpan hasilnya ke tabel kunjungan."""

# Pemilik: Penjelajah. Rujukan: Panduan hlm. 16-21.


def host_dari(url):
    """Kembalikan host URL tanpa www., atau "" kalau URL-nya rusak."""
    # TODO 1 (Minggu 1):
    # Dipakai fitur.py, skor.py, dan bukti.py. Kabari dua anggota lain sebelum mengubahnya.
    ...


def situs_sama(host_a, host_b):
    """True kalau dua host milik situs yang sama, termasuk subdomainnya."""
    # TODO 2 (Minggu 1):
    # Dipakai fitur.py, skor.py, dan bukti.py. Kabari dua anggota lain sebelum mengubahnya.
    ...


async def ambil(session, url, persona, putaran):
    """Satu kunjungan ke satu URL sebagai satu persona; galat dicatat, tidak dilempar."""
    # TODO 3 (Minggu 1):
    # Redirect tidak boleh diikuti otomatis. Redirect di situs yang sama diikuti,
    # redirect ke situs lain hanya dicatat di redirect_ke dan TIDAK dikunjungi.
    # Galat dicatat di kolom catatan. Kembalikan dict berkolom tabel kunjungan.
    ...


async def scan(daftar_url, conn, putaran, jeda):
    """Kunjungi semua URL dengan tiga persona lalu simpan ke tabel kunjungan."""
    # TODO 4 (Minggu 2):
    # Kelompokkan URL per domain. Di dalam satu domain berurutan dan berjeda,
    # antar-domain berjalan bersamaan dengan batas MAKS_DOMAIN_BERSAMAAN.
    # Patuhi robots.txt, coba ulang tanpa cek SSL kalau sertifikat kedaluwarsa,
    # jangan simpan cookie. Simpan tiap kunjungan lewat db.simpan_kunjungan.
    ...

# TODO 5 (Minggu 4):
# Ambil juga halaman selain beranda dari sitemap.xml dan link internal, maksimal 20 per situs.

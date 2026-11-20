"""Mengunjungi setiap URL sebagai tiga persona dan menyimpan hasilnya ke tabel kunjungan."""

# Pemilik: Penjelajah. Rujukan: Panduan hlm. 16-21.

from urllib.parse import urlsplit

import aiohttp
import zlib
import datetime

from . import config  # Biar bisa akses PERSONA, TIMEOUT, dll

def host_dari(url):
    """Kembalikan host URL tanpa www., atau "" kalau URL-nya rusak."""
    # TODO 1 (Minggu 1):
    # Dipakai fitur.py, skor.py, dan bukti.py. Kabari dua anggota lain sebelum mengubahnya.
    host = urlsplit(url).hostname or ""

    if host.startswith("www."):
        host = host[4:]

    return host

def situs_sama(a, b):
    """True kalau dua host milik situs yang sama, termasuk subdomainnya."""
    # TODO 2 (Minggu 1):
    # Dipakai fitur.py, skor.py, dan bukti.py. Kabari dua anggota lain sebelum mengubahnya.
    return host_dari(a) == host_dari(b)

async def ambil(session, url, persona, putaran):
    """Satu kunjungan ke satu URL sebagai satu persona; galat dicatat, tidak dilempar."""
    
    # 1. Ambil setelan dari config.py
    headers = config.PERSONA[persona]
    timeout = aiohttp.ClientTimeout(total=config.TIMEOUT_DETIK)

    # 2. Siapkan wadah kosong (biar kalau error, program nggak crash)
    status_http = None
    html_zlib = None
    url_akhir = url
    redirect_ke = None
    catatan = None

    # 3. Tembak URL-nya!
    try:
        # allow_redirects=False itu WAJIB, biar kita bisa nangkep redirect
        async with session.get(url, headers=headers, timeout=timeout, allow_redirects=False) as resp:
            status_http = resp.status
            teks_html = await resp.text()
            
            # Kompres HTML-nya pakai zlib (sesuai skema database hlm. 5)
            html_zlib = zlib.compress(teks_html.encode("utf-8"))

            # 4. Cek kalau ini redirect (status 3xx)
            if status_http in (301, 302, 303, 307, 308):
                tujuan = resp.headers.get("Location", "")
                # Kalau tujuan masih di situs yang sama, update url_akhir
                if situs_sama(url, tujuan):
                    url_akhir = tujuan
                # Kalau ke situs lain, simpan di redirect_ke (jangan dikunjungi)
                else:
                    redirect_ke = tujuan
                    
    except Exception as e:
        # 5. Kalau timeout atau internet mati, catat pesannya
        catatan = str(e)

    # 6. Kembalikan dalam bentuk dict (sesuai Panduan hlm. 7)
    waktu_sekarang = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    return {
        "putaran": putaran,
        "url": url,
        "domain": host_dari(url),
        "persona": persona,
        "waktu": waktu_sekarang,
        "status": status_http,
        "url_akhir": url_akhir,
        "redirect_ke": redirect_ke,
        "html": html_zlib,
        "catatan": catatan
    }

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

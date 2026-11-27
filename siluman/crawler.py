"""Mengunjungi setiap URL sebagai tiga persona dan menyimpan hasilnya ke tabel kunjungan."""

# Pemilik: Penjelajah. Rujukan: Panduan hlm. 16-21.

from urllib.parse import urlsplit, urljoin

import aiohttp
import zlib
import datetime

from . import config  # Biar bisa akses PERSONA, TIMEOUT, dll


def host_dari(url):
    """Kembalikan nama host huruf kecil tanpa awalan www., atau None jika tidak ada."""

    try:
        host = urlsplit(url).hostname
    except ValueError:
        return None

    if host is None:
        return None

    host = host.lower()
    if host.startswith("www."):
        host = host[4:]

    return host


def situs_sama(host_a, host_b):
    """Kembalikan True jika dua host berada di situs atau subdomain yang sama."""
    if not host_a or not host_b:
        return False

    bersih_a = host_a.lower()
    if bersih_a.startswith("www."):
        bersih_a = bersih_a[4:]

    bersih_b = host_b.lower()
    if bersih_b.startswith("www."):
        bersih_b = bersih_b[4:]

    if bersih_a == bersih_b:
        return True
    if bersih_a.endswith("." + bersih_b):
        return True
    if bersih_b.endswith("." + bersih_a):
        return True

    return False

def kunjungan_kosong(url, persona, putaran):
    """Buat struktur data kunjungan awal dengan nilai kosong sebelum permintaan dilakukan."""
    waktu_sekarang = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "putaran": putaran,
        "url": url,
        "domain": host_dari(url),
        "persona": persona,
        "waktu": waktu_sekarang,
        "status": None,
        "url_akhir": url,
        "redirect_ke": None,
        "html": None,
        "catatan": None,
    }


async def ambil(session, url, persona, putaran):
    """Lakukan satu permintaan HTTP GET tanpa redirect otomatis dan catat hasilnya."""
    data_persona = config.PERSONA[persona]
    if isinstance(data_persona, dict):
        headers = dict(data_persona)
    else:
        headers = {"User-Agent": str(data_persona)}

    timeout = aiohttp.ClientTimeout(total=config.TIMEOUT_DETIK)

    status_http = None
    html_zlib = None
    url_akhir = url
    redirect_ke = None
    catatan = None

    try:
        async with session.get(
            url, headers=headers, timeout=timeout, allow_redirects=False
        ) as resp:
            status_http = resp.status
            teks_html = await resp.text(errors="replace")

            if teks_html:
                html_zlib = zlib.compress(teks_html.encode("utf-8"))

            if status_http in (301, 302, 303, 307, 308):
                lokasi_mentah = resp.headers.get("Location", "")
                if lokasi_mentah:
                    tujuan_penuh = urljoin(url, lokasi_mentah)
                    host_asal = host_dari(url)
                    host_tujuan = host_dari(tujuan_penuh)

                    if situs_sama(host_asal, host_tujuan):
                        url_akhir = tujuan_penuh
                    else:
                        redirect_ke = tujuan_penuh
    except Exception as e:
        catatan = str(e)

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
        "catatan": catatan,
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

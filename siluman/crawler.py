"""Mengunjungi setiap URL sebagai tiga persona dan menyimpan hasilnya ke tabel kunjungan."""

# Pemilik: Penjelajah. Rujukan: Panduan hlm. 16-21.


from urllib.parse import urljoin, urlsplit
import asyncio
import datetime
import zlib

import aiohttp

from . import config
from . import db


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


async def baca_isi(resp):
    """Baca isi respons HTTP hingga batas ukuran konfigurasi lalu kembalikan teksnya."""
    potongan_byte = bytearray()
    batas = config.BATAS_UKURAN

    async for chunk in resp.content.iter_chunked(65536):
        sisa_kuota = batas - len(potongan_byte)
        if sisa_kuota <= 0:
            break
        potongan_byte.extend(chunk[:sisa_kuota])

    if not potongan_byte:
        return ""

    return potongan_byte.decode("utf-8", errors="replace")


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
            teks_html = await baca_isi(resp)

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


async def boleh_kunjungi_robots(session, url, persona, cache_robots):
    """Periksa apakah URL diizinkan oleh robots.txt untuk persona yang dipakai."""
    host = host_dari(url)
    if not host:
        return False

    parsed = urlsplit(url)
    if not parsed.scheme:
        return False

    url_robots = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if url_robots not in cache_robots:
        aturan = {}
        try:
            timeout = aiohttp.ClientTimeout(total=config.TIMEOUT_DETIK)
            async with session.get(url_robots, timeout=timeout, allow_redirects=True) as resp:
                if resp.status == 200:
                    teks_robots = await baca_isi(resp)
                    agent_aktif = "*"
                    for baris in teks_robots.splitlines():
                        bersih = baris.split("#", 1)[0].strip()
                        if not bersih:
                            continue
                        if ":" not in bersih:
                            continue
                        kunci, nilai = bersih.split(":", 1)
                        kunci = kunci.strip().lower()
                        nilai = nilai.strip()
                        if kunci == "user-agent":
                            agent_aktif = nilai.lower()
                            if agent_aktif not in aturan:
                                aturan[agent_aktif] = []
                        elif kunci == "disallow" and nilai:
                            if agent_aktif not in aturan:
                                aturan[agent_aktif] = []
                            aturan[agent_aktif].append(nilai)
        except Exception:
            aturan = {}
        cache_robots[url_robots] = aturan

    aturan_situs = cache_robots[url_robots]
    daftar_larangan = []
    if "*" in aturan_situs:
        daftar_larangan.extend(aturan_situs["*"])

    ua_persona = str(config.PERSONA[persona].get("User-Agent", "")).lower() if isinstance(config.PERSONA[persona], dict) else str(config.PERSONA[persona]).lower()
    for agen, path_dilarang in aturan_situs.items():
        if agen != "*" and agen in ua_persona:
            daftar_larangan.extend(path_dilarang)

    path_url = parsed.path or "/"
    for prefix_larangan in daftar_larangan:
        if prefix_larangan == "/":
            return False
        if path_url.startswith(prefix_larangan):
            return False

    return True


async def kunjungi_url_persona(session, url, persona, putaran, cache_robots):
    """Kunjungi satu URL untuk satu persona dengan dukungan robots.txt, redirect, dan retry SSL."""
    diizinkan = await boleh_kunjungi_robots(session, url, persona, cache_robots)
    if not diizinkan:
        data_blokir = kunjungan_kosong(url, persona, putaran)
        data_blokir["catatan"] = "diblokir robots.txt"
        return data_blokir

    url_sekarang = url
    lompatan = 0
    hasil_terakhir = None

    while True:
        hasil = await ambil(session, url_sekarang, persona, putaran)

        if hasil["catatan"] and ("SSL" in hasil["catatan"] or "certificate" in hasil["catatan"].lower()):
            data_persona = config.PERSONA[persona]
            if isinstance(data_persona, dict):
                headers = dict(data_persona)
            else:
                headers = {"User-Agent": str(data_persona)}

            timeout = aiohttp.ClientTimeout(total=config.TIMEOUT_DETIK)
            try:
                async with session.get(
                    url_sekarang,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=False,
                    ssl=False,
                ) as resp_ssl:
                    status_ssl = resp_ssl.status
                    teks_ssl = await baca_isi(resp_ssl)
                    html_ssl = None
                    if teks_ssl:
                        html_ssl = zlib.compress(teks_ssl.encode("utf-8"))

                    url_akhir_ssl = url_sekarang
                    redirect_ke_ssl = None
                    if status_ssl in (301, 302, 303, 307, 308):
                        lokasi_mentah = resp_ssl.headers.get("Location", "")
                        if lokasi_mentah:
                            tujuan_penuh = urljoin(url_sekarang, lokasi_mentah)
                            if situs_sama(host_dari(url_sekarang), host_dari(tujuan_penuh)):
                                url_akhir_ssl = tujuan_penuh
                            else:
                                redirect_ke_ssl = tujuan_penuh

                    hasil["status"] = status_ssl
                    hasil["html"] = html_ssl
                    hasil["url_akhir"] = url_akhir_ssl
                    hasil["redirect_ke"] = redirect_ke_ssl
                    hasil["catatan"] = "retry ssl=False"
            except Exception as e_ssl:
                hasil["catatan"] = f"ssl retry gagal: {e_ssl}"

        hasil["url"] = url
        hasil["domain"] = host_dari(url)
        hasil_terakhir = hasil

        if hasil["redirect_ke"] is not None:
            break

        if hasil["url_akhir"] != url_sekarang:
            if lompatan >= config.MAKS_LOMPATAN_REDIRECT:
                hasil_terakhir["catatan"] = "batas lompatan redirect tercapai"
                break
            lompatan = lompatan + 1
            url_sekarang = hasil["url_akhir"]
        else:
            break

    return hasil_terakhir


async def scan(daftar_url, conn, putaran, jeda):
    """Kunjungi semua URL dengan tiga persona lalu simpan ke tabel kunjungan."""
    if jeda is None:
        jeda_aktif = config.JEDA_PER_DOMAIN
    else:
        jeda_aktif = jeda

    kelompok_domain = {}
    for url in daftar_url:
        host = host_dari(url)
        if not host:
            continue
        if host not in kelompok_domain:
            kelompok_domain[host] = []
        if url not in kelompok_domain[host]:
            kelompok_domain[host].append(url)

    semaphore = asyncio.Semaphore(config.MAKS_DOMAIN_BERSAMAAN)
    cache_robots = {}

    async def proses_satu_domain(host_domain, daftar_url_domain):
        async with semaphore:
            sudah_ada_kunjungan = False
            for url_item in daftar_url_domain:
                for persona in config.URUTAN_PERSONA:
                    if sudah_ada_kunjungan and jeda_aktif > 0:
                        await asyncio.sleep(jeda_aktif)

                    hasil = await kunjungi_url_persona(
                        session, url_item, persona, putaran, cache_robots
                    )
                    db.simpan_kunjungan(conn, hasil)
                    sudah_ada_kunjungan = True

    cookie_jar = aiohttp.DummyCookieJar()
    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
        tugas = []
        for host_domain, daftar_url_domain in kelompok_domain.items():
            tugas.append(proses_satu_domain(host_domain, daftar_url_domain))

        if tugas:
            await asyncio.gather(*tugas)


# TODO 5 (Minggu 4):
# Ambil juga halaman selain beranda dari sitemap.xml dan link internal, maksimal 20 per situs.
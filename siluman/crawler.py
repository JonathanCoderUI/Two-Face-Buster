"""Modul Penjelajah (crawler): mengambil halaman dengan 3 persona secara sopan."""

import asyncio
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp

from siluman import config, db

STATUS_REDIRECT = [301, 302, 303, 307, 308]


def kunjungan_kosong(url, persona, putaran):
    """Membuat struktur data kunjungan awal dengan nilai default/kosong."""
    return {
        "putaran": putaran,
        "url": url,
        "domain": host_dari(url),
        "persona": persona,
        "waktu": "",
        "status": None,
        "url_akhir": None,
        "redirect_ke": None,
        "html": None,
        "catatan": None,
    }


def host_dari(url):
    """Mengambil hostname tanpa awalan 'www.' dari URL; mengembalikan string kosong jika gagal."""
    if not url:
        return ""
    try:
        host = urlparse(url).hostname
    except ValueError:
        return ""
    if host is None:
        return ""
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def situs_sama(host_a, host_b):
    """Mengembalikan True jika dua host berada pada situs/domain yang sama (termasuk subdomain)."""
    if host_a == "" or host_b == "":
        return False
    if host_a == host_b:
        return True
    if host_a.endswith("." + host_b) or host_b.endswith("." + host_a):
        return True
    return False


async def baca_isi(resp):
    """Membaca body respons maksimal BATAS_UKURAN byte lalu mendekodekannya menjadi teks."""
    potongan = []
    total = 0
    async for bagian in resp.content.iter_chunked(65536):
        potongan.append(bagian)
        total = total + len(bagian)
        if total >= config.BATAS_UKURAN:
            break
    data = b"".join(potongan)
    charset = resp.charset
    if charset is None:
        charset = "utf-8"
    try:
        return data.decode(charset, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


async def ambil(session, url, persona, putaran, cek_ssl=True):
    """Melakukan satu kunjungan ke satu URL sebagai satu persona; mencatat galat tanpa melempar."""
    hasil = kunjungan_kosong(url, persona, putaran)
    header = config.PERSONA[persona]
    sekarang = url
    lompatan = 0
    selesai = False
    try:
        while not selesai:
            async with session.get(
                sekarang,
                headers=header,
                allow_redirects=False,
                ssl=cek_ssl,
            ) as resp:
                hasil["status"] = resp.status
                lokasi = resp.headers.get("Location")
                if resp.status in STATUS_REDIRECT and lokasi is not None:
                    tujuan = urljoin(sekarang, lokasi)
                    if not situs_sama(host_dari(tujuan), hasil["domain"]):
                        hasil["redirect_ke"] = tujuan
                        selesai = True
                    elif lompatan >= config.MAKS_LOMPATAN_REDIRECT:
                        hasil["catatan"] = "redirect berputar"
                        selesai = True
                    else:
                        lompatan = lompatan + 1
                        sekarang = tujuan
                else:
                    hasil["html"] = await baca_isi(resp)
                    selesai = True
        hasil["url_akhir"] = sekarang
    except aiohttp.ClientSSLError:
        hasil["catatan"] = "ssl"
    except asyncio.TimeoutError:
        hasil["catatan"] = "timeout"
    except aiohttp.ClientError as e:
        hasil["catatan"] = type(e).__name__ + ": " + str(e)
    except ValueError as e:
        hasil["catatan"] = "url tidak valid: " + str(e)
    return hasil


async def baca_robots(session, url, putaran):
    """Mengambil dan mem-parse robots.txt situs; mengizinkan semua jika tidak tersedia."""
    k = await ambil(session, urljoin(url, "/robots.txt"), "browser", putaran, cek_ssl=False)
    robots = RobotFileParser()
    if k["status"] == 200 and k["html"] is not None:
        robots.parse(k["html"].splitlines())
    else:
        robots.parse([])
    return robots


async def jelajahi_domain(session, daftar, semafor, conn, putaran, jeda):
    """Menjelajahi seluruh URL pada satu domain secara berurutan dengan jeda antar-permintaan."""
    async with semafor:
        robots = await baca_robots(session, daftar[0], putaran)
        await asyncio.sleep(jeda)
        for url in daftar:
            boleh = robots.can_fetch("*", url)
            for persona in config.URUTAN_PERSONA:
                if boleh:
                    hasil = await ambil(session, url, persona, putaran)
                    if hasil["catatan"] == "ssl":
                        hasil = await ambil(session, url, persona, putaran, cek_ssl=False)
                        if hasil["catatan"] is None:
                            hasil["catatan"] = "sertifikat SSL tidak valid"
                    await asyncio.sleep(jeda)
                else:
                    hasil = kunjungan_kosong(url, persona, putaran)
                    hasil["catatan"] = "dilarang robots.txt"
                db.simpan_kunjungan(conn, hasil)


async def scan(daftar_url, conn, putaran, jeda=config.JEDA_PER_DOMAIN):
    """Menjalankan pemindaian daftar URL lintas domain secara asinkron."""
    per_domain = {}
    for url in daftar_url:
        domain = host_dari(url)
        if domain not in per_domain:
            per_domain[domain] = []
        per_domain[domain].append(url)

    semafor = asyncio.Semaphore(config.MAKS_DOMAIN_BERSAMAAN)
    timeout = aiohttp.ClientTimeout(total=config.TIMEOUT_DETIK)

    async with aiohttp.ClientSession(
        timeout=timeout,
        cookie_jar=aiohttp.DummyCookieJar(),
    ) as session:
        tugas = []
        for domain in per_domain:
            tugas.append(
                asyncio.create_task(
                    jelajahi_domain(session, per_domain[domain], semafor, conn, putaran, jeda)
                )
            )
        selesai = 0
        for berikutnya in asyncio.as_completed(tugas):
            try:
                await berikutnya
            except Exception as e:
                print("Galat tak terduga:", repr(e))
            selesai = selesai + 1
            if selesai % 50 == 0 or selesai == len(tugas):
                print("Selesai", selesai, "dari", len(tugas), "domain")
import asyncio
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp

from siluman import config, db

STATUS_REDIRECT = [301, 302, 303, 307, 308]


def host_dari(url):
    """'https://www.Sekolah.sch.id/berita' -> 'sekolah.sch.id'"""
    try:
        host = urlparse(url).hostname
    except ValueError:  # URL rusak, mis. dari header Location yang aneh
        return ""
    if host == None:
        return ""
    if host.startswith("www."):  # noqa: FURB188
        host = host[4:]
    return host


def situs_sama(host_a, host_b):
    """True kalau dua host milik situs yang sama, termasuk subdomainnya."""
    if host_a == "" or host_b == "":
        return False
    if host_a == host_b:
        return True
    if host_a.endswith("." + host_b) or host_b.endswith("." + host_a):  # noqa: SIM103
        return True
    return False


def kunjungan_kosong(url, persona, putaran):
    """Buat dict berkolom tabel kunjungan dengan nilai hasil awal None."""
    return {
        "putaran": putaran,
        "url": url,
        "domain": host_dari(url),
        "persona": persona,
        "waktu": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
        "status": None,
        "url_akhir": None,
        "redirect_ke": None,
        "html": None,
        "catatan": None,
    }


async def baca_isi(resp):
    """Baca body maksimal BATAS_UKURAN byte, lalu ubah jadi teks."""
    potongan = []
    total = 0
    async for bagian in resp.content.iter_chunked(65536):
        potongan.append(bagian)
        total = total + len(bagian)
        if total >= config.BATAS_UKURAN:
            break
    data = b"".join(potongan)
    charset = resp.charset
    if charset == None:
        charset = "utf-8"
    try:
        return data.decode(charset, errors="replace")
    except LookupError:  # server menyebut charset yang tidak dikenal Python
        return data.decode("utf-8", errors="replace")


async def ambil(session, url, persona, putaran, cek_ssl=True):
    """Satu kunjungan ke satu URL sebagai satu persona. Galat dicatat, tidak dilempar."""
    hasil = kunjungan_kosong(url, persona, putaran)
    header = config.PERSONA[persona]
    sekarang = url
    lompatan = 0
    selesai = False
    try:
        while not selesai:
            async with session.get(
                sekarang, headers=header, allow_redirects=False, ssl=cek_ssl
            ) as resp:
                hasil["status"] = resp.status
                lokasi = resp.headers.get("Location")
                if resp.status in STATUS_REDIRECT and lokasi != None:
                    tujuan = urljoin(sekarang, lokasi)
                    if not situs_sama(host_dari(tujuan), hasil["domain"]):
                        hasil["redirect_ke"] = tujuan  # situs lain: dicatat, TIDAK dikunjungi
                        selesai = True
                    elif lompatan >= config.MAKS_LOMPATAN_REDIRECT:
                        hasil["catatan"] = "redirect berputar"
                        selesai = True
                    else:  # masih situs yang sama: ikuti
                        sekarang = tujuan
                        lompatan = lompatan + 1
                else:
                    hasil["html"] = await baca_isi(resp)
                    selesai = True
        hasil["url_akhir"] = sekarang
    except aiohttp.ClientSSLError:
        hasil["catatan"] = "ssl"
    except asyncio.TimeoutError:  # noqa: UP041
        hasil["catatan"] = "timeout"
    except aiohttp.ClientError as e:
        hasil["catatan"] = type(e).__name__ + ": " + str(e)
    except ValueError as e:
        hasil["catatan"] = "url tidak valid: " + str(e)
    return hasil


async def baca_robots(session, url, putaran):
    """robots.txt situs. Kalau tidak ada atau gagal diambil, semua halaman dianggap boleh."""
    k = await ambil(session, urljoin(url, "/robots.txt"), "browser", putaran, cek_ssl=False)
    robots = RobotFileParser()
    if k["status"] == 200 and k["html"] != None:
        robots.parse(k["html"].splitlines())
    else:
        robots.parse([])
    return robots


async def jelajahi_domain(session, daftar, semafor, conn, putaran, jeda):
    """Semua URL milik SATU domain, berurutan dan berjeda, supaya server mereka tidak terbebani."""
    async with semafor:
        robots = await baca_robots(session, daftar[0], putaran)
        await asyncio.sleep(jeda)
        for url in daftar:
            boleh = robots.can_fetch("*", url)
            for persona in config.URUTAN_PERSONA:
                if boleh:
                    hasil = await ambil(session, url, persona, putaran)
                    if hasil["catatan"] == "ssl":
                        # Banyak situs lembaga sertifikatnya kedaluwarsa: tetap dibaca, tapi dicatat.
                        hasil = await ambil(session, url, persona, putaran, cek_ssl=False)
                        if hasil["catatan"] == None:
                            hasil["catatan"] = "sertifikat SSL tidak valid"
                    await asyncio.sleep(jeda)
                else:
                    hasil = kunjungan_kosong(url, persona, putaran)
                    hasil["catatan"] = "dilarang robots.txt"
                db.simpan_kunjungan(conn, hasil)


async def scan(daftar_url, conn, putaran, jeda=config.JEDA_PER_DOMAIN):
    per_domain = {}
    for url in daftar_url:
        domain = host_dari(url)
        if domain not in per_domain:
            per_domain[domain] = []
        per_domain[domain].append(url)

    semafor = asyncio.Semaphore(config.MAKS_DOMAIN_BERSAMAAN)
    timeout = aiohttp.ClientTimeout(total=config.TIMEOUT_DETIK)

    # DummyCookieJar: cookie tidak disimpan, jadi setiap kunjungan seperti pengunjung baru.
    async with aiohttp.ClientSession(
        timeout=timeout, cookie_jar=aiohttp.DummyCookieJar()
    ) as session:
        tugas = []
        for domain in per_domain:  # noqa: PLC0206
            tugas.append(
                asyncio.create_task(
                    jelajahi_domain(session, per_domain[domain], semafor, conn, putaran, jeda)
                )
            )
        selesai = 0
        for berikutnya in asyncio.as_completed(tugas):
            try:
                await berikutnya
            except Exception as e:  # noqa: BLE001
                print("Galat tak terduga:", repr(e))
            selesai = selesai + 1
            if selesai % 50 == 0 or selesai == len(tugas):
                print("Selesai", selesai, "dari", len(tugas), "domain")
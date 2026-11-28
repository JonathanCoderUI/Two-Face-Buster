"""Tes untuk crawler.py."""

# Pemilik: Penjelajah.

import asyncio
import socket
import threading

import aiohttp
import pytest
from flask import Flask, Response
from werkzeug.serving import make_server

from siluman import config, crawler

ALAMAT_JUDOL = "http://slot-gacor-uji.invalid/daftar"


def test_host_dari():
    assert crawler.host_dari("https://www.Sekolah.sch.id/berita") == "sekolah.sch.id"
    assert crawler.host_dari("http://sekolah.sch.id:8080/") == "sekolah.sch.id"
    assert crawler.host_dari("https://berita.sekolah.sch.id/") == "berita.sekolah.sch.id"


def test_host_dari_url_rusak():
    assert crawler.host_dari("") == ""
    assert crawler.host_dari("bukan url") == ""
    # Kurung siku tak berpasangan membuat urlparse melempar ValueError.
    assert crawler.host_dari("http://[::1/") == ""


def test_situs_sama():
    assert crawler.situs_sama("sekolah.sch.id", "sekolah.sch.id") == True
    # Subdomain dianggap situs yang sama, ke dua arah.
    assert crawler.situs_sama("berita.sekolah.sch.id", "sekolah.sch.id") == True
    assert crawler.situs_sama("sekolah.sch.id", "berita.sekolah.sch.id") == True


def test_situs_sama_berbeda_atau_kosong():
    assert crawler.situs_sama("sekolah.sch.id", "kampus.ac.id") == False
    # Akhiran nama yang kebetulan sama bukan subdomain.
    assert crawler.situs_sama("xsekolah.sch.id", "sekolah.sch.id") == False
    assert crawler.situs_sama("", "sekolah.sch.id") == False
    assert crawler.situs_sama("sekolah.sch.id", "") == False
    assert crawler.situs_sama("", "") == False


async def kunjungi(url, persona, batas_detik=10):
    """Satu kunjungan lewat crawler.ambil dengan sesi baru."""
    timeout = aiohttp.ClientTimeout(total=batas_detik)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        return await crawler.ambil(session, url, persona, putaran=1)


def port_mati():
    """Cari port lokal yang tidak ada servernya."""
    soket = socket.socket()
    soket.bind(("127.0.0.1", 0))
    port = soket.getsockname()[1]
    soket.close()
    return port


def test_server_mati_dicatat():
    hasil = asyncio.run(kunjungi("http://127.0.0.1:" + str(port_mati()) + "/", "browser"))
    assert hasil["status"] == None
    assert hasil["html"] == None
    assert hasil["catatan"] != None


def test_server_lambat_timeout(alamat_uji):
    hasil = asyncio.run(kunjungi(alamat_uji + "/lambat/1", "browser", batas_detik=1))
    assert hasil["catatan"] == "timeout"
    assert hasil["html"] == None


def test_redirect_ke_situs_lain_tidak_diikuti(alamat_uji):
    hasil = asyncio.run(kunjungi(alamat_uji + "/cloak-referer/1", "dari_google"))
    assert hasil["status"] == 302
    assert hasil["redirect_ke"] == ALAMAT_JUDOL
    assert hasil["html"] == None
    assert hasil["catatan"] == None


def test_persona_lain_tidak_dialihkan(alamat_uji):
    for persona in ["browser", "googlebot"]:
        hasil = asyncio.run(kunjungi(alamat_uji + "/cloak-referer/1", persona))
        assert hasil["status"] == 200
        assert hasil["redirect_ke"] == None
        assert "SMA Negeri Contoh" in hasil["html"]


def test_googlebot_dan_browser_beda_isi(alamat_uji):
    bot = asyncio.run(kunjungi(alamat_uji + "/cloak-ua/1", "googlebot"))
    biasa = asyncio.run(kunjungi(alamat_uji + "/cloak-ua/1", "browser"))
    assert "CONTOH UJI" in bot["html"]
    assert "CONTOH UJI" not in biasa["html"]


# Situs kecil khusus tes redirect di situs yang sama, yang tidak ada di situs uji.
situs_redirect = Flask("situs_redirect")


@situs_redirect.route("/a")
def lompat_a():
    return Response("", status=302, headers={"Location": "/b"})


@situs_redirect.route("/b")
def tujuan_b():
    return "isi tujuan"


@situs_redirect.route("/putar")
def putar():
    return Response("", status=302, headers={"Location": "/putar"})


@pytest.fixture(scope="module")
def alamat_redirect():
    server = make_server("127.0.0.1", 0, situs_redirect, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:" + str(server.server_port)
    server.shutdown()
    server.server_close()


def test_redirect_di_situs_sama_diikuti(alamat_redirect):
    hasil = asyncio.run(kunjungi(alamat_redirect + "/a", "browser"))
    assert hasil["status"] == 200
    assert hasil["html"] == "isi tujuan"
    assert hasil["redirect_ke"] == None
    assert hasil["url_akhir"] == alamat_redirect + "/b"


def test_redirect_berputar_dihentikan(alamat_redirect):
    hasil = asyncio.run(kunjungi(alamat_redirect + "/putar", "browser"))
    assert hasil["catatan"] == "redirect berputar"
    assert hasil["html"] == None


class AliranPalsu:
    """Pengganti resp.content: mengeluarkan potongan byte yang sudah ditentukan."""

    def __init__(self, daftar_potongan):
        self.daftar_potongan = daftar_potongan

    async def iter_chunked(self, ukuran):
        for potongan in self.daftar_potongan:
            yield potongan


class RespPalsu:
    """Pengganti objek respons aiohttp: hanya content dan charset yang dipakai baca_isi."""

    def __init__(self, daftar_potongan, charset):
        self.content = AliranPalsu(daftar_potongan)
        self.charset = charset


def test_baca_isi_dipotong_di_batas(monkeypatch):
    monkeypatch.setattr(config, "BATAS_UKURAN", 100)
    resp = RespPalsu([b"a" * 80, b"b" * 80, b"c" * 80], "utf-8")
    isi = asyncio.run(crawler.baca_isi(resp))
    assert len(isi) == 100


def test_baca_isi_charset_tidak_dikenal():
    resp = RespPalsu(["halo dunia".encode("utf-8")], "charset-ngawur")
    assert asyncio.run(crawler.baca_isi(resp)) == "halo dunia"


def test_baca_isi_tanpa_charset_dianggap_utf8():
    resp = RespPalsu(["sekolah é".encode("utf-8")], None)
    assert asyncio.run(crawler.baca_isi(resp)) == "sekolah é"

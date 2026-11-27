"""Tes untuk fitur.py."""

# Pemilik: Detektif.

from urllib.parse import urlsplit

import pytest
from bs4 import BeautifulSoup

from siluman import fitur
from siluman.fitur import (
    cari_teks_tersembunyi,
    ekstrak_teks,
    ekstrak_teks_terlihat,
    kemiripan,
    nama_domain_berbau_judol,
    skrip_pengalih_referrer,
)
from tests.helper_situs_uji import ambil_versi

URL_SITUS = "https://sma-contoh.sch.id/"


def test_kemiripan_teks_identik():
    teks = "Penerimaan peserta didik baru dibuka tanggal 1 Juni"
    assert kemiripan(teks, teks) == 1.0


def test_kemiripan_dihitung_per_kata():
    # Blok cocok: "kucing" dan "di atas" -> M = 3, T = 10, rasio 2 x 3 / 10.
    a = "kucing tidur di atas sofa"
    b = "kucing duduk di atas meja"
    assert abs(kemiripan(a, b) - 0.6) < 0.001


def test_kemiripan_teks_berbeda_total():
    assert kemiripan("berita sekolah hari ini", "slot gacor maxwin") == 0.0


def kemiripan_browser_googlebot(alamat, jalur):
    """Kunjungi satu jalur dan kembalikan kemiripan teks versi browser dan Googlebot."""
    versi = ambil_versi(alamat, jalur)
    teks_browser = ekstrak_teks(versi["browser"]["html"])
    teks_googlebot = ekstrak_teks(versi["googlebot"]["html"])
    return kemiripan(teks_browser, teks_googlebot)


def test_kemiripan_situs_uji(alamat_uji):
    # Target di spesifikasi: /cloak-ua/1 sekitar 0,37 dan /dinamis/1 sekitar 0,85.
    cloak = kemiripan_browser_googlebot(alamat_uji, "/cloak-ua/1")
    assert 0.30 <= cloak <= 0.45
    dinamis = kemiripan_browser_googlebot(alamat_uji, "/dinamis/1")
    assert 0.80 <= dinamis <= 0.90


def test_ekstrak_teks_ambil_meta_buang_script():
    html = (
        "<html><head><title>SMA Contoh</title>"
        '<meta name="description" content="Situs resmi sekolah">'
        "<style>body { color: red }</style></head>"
        "<body><h1>Berita</h1>\n\n<p>Upacara   hari Senin</p>"
        "<script>var rahasia = 'jangan terbaca';</script></body></html>"
    )
    teks = ekstrak_teks(html)
    assert teks == "SMA Contoh Situs resmi sekolah Berita Upacara hari Senin"


def test_ekstrak_teks_tanpa_judul_dan_meta():
    assert ekstrak_teks("<p>Hanya isi</p>") == "Hanya isi"


def test_ekstrak_teks_kosong():
    assert ekstrak_teks("") == ""
    assert ekstrak_teks(None) == ""


def test_teks_tersembunyi_tertangkap():
    html = (
        "<p>Berita sekolah</p>"
        '<div style="display:none">slot gacor, slot online, dan bonus new member</div>'
    )
    temuan = cari_teks_tersembunyi(html, URL_SITUS)
    assert len(temuan) == 1
    assert temuan[0]["frasa"] == ["bonus new member", "slot gacor", "slot online"]


def test_semua_cara_menyembunyikan_tertangkap():
    gaya_gaya = [
        "display: none !important",
        "visibility:hidden",
        "font-size:0",
        "font-size: 0px",
        "opacity:0",
        "position:absolute; left:-9999px",
        "text-indent:-9999px",
    ]
    for gaya in gaya_gaya:
        html = '<div style="' + gaya + '">slot gacor</div>'
        assert len(cari_teks_tersembunyi(html, URL_SITUS)) == 1, gaya
    assert len(cari_teks_tersembunyi("<div hidden>slot gacor</div>", URL_SITUS)) == 1


def test_gaya_yang_tidak_menyembunyikan_diabaikan():
    gaya_gaya = [
        "font-size:0.9em",
        "font-size:12px",
        "opacity:0.5",
        "left:-10px",
        "display:block",
        "visibility:visible",
    ]
    for gaya in gaya_gaya:
        html = '<div style="' + gaya + '">slot gacor</div>'
        assert cari_teks_tersembunyi(html, URL_SITUS) == [], gaya


def test_menu_tersembunyi_biasa_diabaikan():
    html = (
        '<ul style="display:none">'
        '<li><a href="/profil">Profil</a></li>'
        '<li><a href="https://sma-contoh.sch.id/kontak">Kontak</a></li>'
        '<li><a href="https://www.facebook.com/sma">Facebook</a></li>'
        "</ul>"
    )
    assert cari_teks_tersembunyi(html, URL_SITUS) == []


def host_palsu(url):
    """Pengganti crawler.host_dari untuk tes: host URL, atau "" kalau tidak ada."""
    host = urlsplit(url).hostname
    if host == None:
        return ""
    return host


def situs_sama_palsu(host_a, host_b):
    """Pengganti crawler.situs_sama untuk tes: host sama atau salah satunya subdomain yang lain."""
    if host_a == "" or host_b == "":
        return False
    if host_a == host_b:
        return True
    if host_a.endswith("." + host_b) or host_b.endswith("." + host_a):
        return True
    return False


def test_link_luar_dibandingkan_per_host(monkeypatch):
    # situs_sama menerima HOST, bukan URL lengkap. Link ke host sendiri, subdomainnya,
    # dan link tanpa skema (//) tidak boleh dihitung sebagai link luar.
    monkeypatch.setattr(fitur, "host_dari", host_palsu, raising=False)
    monkeypatch.setattr(fitur, "situs_sama", situs_sama_palsu)
    html = (
        "<div>"
        '<a href="https://sma-contoh.sch.id/kontak">kontak</a>'
        '<a href="https://berita.sma-contoh.sch.id/">berita</a>'
        '<a href="//sma-contoh.sch.id/profil">profil</a>'
        '<a href="https://situs-lain.com/">lain</a>'
        "</div>"
    )
    tag = BeautifulSoup(html, "html.parser").find("div")
    assert fitur.hitung_link_luar(tag, URL_SITUS) == 1


def test_tiga_link_luar_tersembunyi_dilaporkan():
    html = (
        '<div hidden>'
        '<a href="https://a-situs.com/">a</a>'
        '<a href="https://b-situs.com/">b</a>'
        '<a href="http://c-situs.com/">c</a>'
        "</div>"
    )
    temuan = cari_teks_tersembunyi(html, URL_SITUS)
    assert len(temuan) == 1
    assert temuan[0]["link_luar"] == 3
    assert temuan[0]["frasa"] == []


def test_elemen_bersarang_hanya_dilaporkan_sekali():
    html = '<div style="display:none"><p style="font-size:0">slot gacor</p></div>'
    assert len(cari_teks_tersembunyi(html, URL_SITUS)) == 1


def test_tersembunyi_tanpa_html():
    assert cari_teks_tersembunyi(None, URL_SITUS) == []
    assert cari_teks_tersembunyi("", URL_SITUS) == []


def test_ekstrak_teks_terlihat_membuang_elemen_tersembunyi():
    html = (
        "<title>SMA Contoh</title><p>Berita sekolah</p>"
        '<div style="display:none"><span style="opacity:0">slot gacor</span></div>'
    )
    assert ekstrak_teks_terlihat(html) == "SMA Contoh Berita sekolah"
    assert "slot gacor" in ekstrak_teks(html)


def test_skrip_pengalih_tertangkap():
    html = (
        "<script>"
        'if (document.referrer.indexOf("google") > -1) { window.location.href = "https://slot-gacor88.com"; }'
        "</script>"
    )
    assert skrip_pengalih_referrer(html) == True


def test_skrip_pengalih_dengan_replace_dan_ejaan_referer():
    html = (
        "<script>"
        'var asal = document.referer; if (/google/.test(asal)) { location.replace("https://x.com"); }'
        "</script>"
    )
    assert skrip_pengalih_referrer(html) == True


def test_skrip_biasa_tidak_dianggap_pengalih():
    # Analitik membaca referrer dan menyebut google, tapi tidak memindahkan halaman.
    html_analitik = (
        "<script>"
        'var asal = document.referrer; var host = window.location.hostname; '
        'var url = "https://www.google-analytics.com/collect?r=" + asal;'
        "</script>"
    )
    assert skrip_pengalih_referrer(html_analitik) == False
    # Memindahkan halaman tanpa memeriksa asal bukan tanda ini.
    html_pindah_saja = '<script>window.location.href = "https://google.com";</script>'
    assert skrip_pengalih_referrer(html_pindah_saja) == False
    # Perbandingan (==) bukan pemindahan.
    html_bandingkan = (
        '<script>if (document.referrer == "google" && location.href == "x") { alert(1); }</script>'
    )
    assert skrip_pengalih_referrer(html_bandingkan) == False


def test_skrip_pengalih_tanpa_html():
    assert skrip_pengalih_referrer(None) == False
    assert skrip_pengalih_referrer("") == False


def test_domain_berbau_judol_tertangkap():
    assert nama_domain_berbau_judol("https://slot-gacor88.com/daftar") == True
    assert nama_domain_berbau_judol("http://TOGEL4D.NET") == True
    assert nama_domain_berbau_judol("https://slot.kampus-contoh.ac.id/") == True


def test_domain_judol_samaran_tetap_tertangkap():
    assert nama_domain_berbau_judol("https://s1otgac0r.com/") == True


def test_domain_biasa_tidak_tertangkap():
    assert nama_domain_berbau_judol("https://sma-contoh.sch.id/berita") == False
    assert nama_domain_berbau_judol("https://www.google.com/") == False


def test_kata_judol_di_path_tidak_dihitung():
    assert nama_domain_berbau_judol("https://sma-contoh.sch.id/slot-gacor") == False


def test_domain_kosong_atau_rusak():
    assert nama_domain_berbau_judol("") == False
    assert nama_domain_berbau_judol(None) == False
    assert nama_domain_berbau_judol("bukan url") == False

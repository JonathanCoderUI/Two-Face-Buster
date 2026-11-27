"""Tes untuk situs_uji/app.py: setiap halaman harus berperilaku seperti yang dijanjikan."""

# Pemilik: Pelapor.

import re
from urllib.parse import urlsplit

import pytest

from siluman.fitur import ekstrak_teks, ekstrak_teks_terlihat
from siluman.normalisasi import cari_frasa
from tests.helper_situs_uji import ambil_mentah

PERSONA_SEMUA = ["browser", "googlebot", "dari_google"]


def isi_halaman(alamat, jalur, persona):
    """Kembalikan isi HTML satu jalur untuk satu persona, setelah memastikan statusnya 200."""
    status, lokasi, isi = ambil_mentah(alamat, jalur, persona)
    assert status == 200
    return isi


def test_halaman_jujur_sama_untuk_semua_persona(alamat_uji):
    for jalur in ["/normal/1", "/edukasi/1", "/tersembunyi/1", "/terbuka/1"]:
        isi_browser = isi_halaman(alamat_uji, jalur, "browser")
        assert isi_halaman(alamat_uji, jalur, "googlebot") == isi_browser, jalur
        assert isi_halaman(alamat_uji, jalur, "dari_google") == isi_browser, jalur


def test_nomor_halaman_mengubah_pengumuman(alamat_uji):
    assert isi_halaman(alamat_uji, "/normal/1", "browser") != isi_halaman(alamat_uji, "/normal/2", "browser")


def test_cloak_ua_judol_hanya_untuk_googlebot(alamat_uji):
    isi_bot = isi_halaman(alamat_uji, "/cloak-ua/1", "googlebot")
    assert "CONTOH UJI" in isi_bot
    assert len(cari_frasa(ekstrak_teks(isi_bot))) >= 3
    for persona in ["browser", "dari_google"]:
        isi = isi_halaman(alamat_uji, "/cloak-ua/1", persona)
        assert "CONTOH UJI" not in isi
        assert cari_frasa(ekstrak_teks(isi)) == {}


def test_cloak_samaran_butuh_normalisasi(alamat_uji):
    isi_bot = isi_halaman(alamat_uji, "/cloak-samaran/1", "googlebot")
    teks = ekstrak_teks(isi_bot)
    assert "CONTOH UJI" in isi_bot
    # Ejaan samaran: tanpa normalisasi, frasa polos tidak ada di teksnya.
    assert "slot gacor" not in teks.lower()
    assert len(cari_frasa(teks)) >= 3


def test_cloak_referer_hanya_mengalihkan_pengunjung_dari_google(alamat_uji):
    status, lokasi, isi = ambil_mentah(alamat_uji, "/cloak-referer/1", "dari_google")
    assert status == 302
    assert lokasi == "http://slot-gacor-uji.invalid/daftar"
    for persona in ["browser", "googlebot"]:
        status, lokasi, isi = ambil_mentah(alamat_uji, "/cloak-referer/1", persona)
        assert status == 200
        assert lokasi == None


def test_tersembunyi_judol_tidak_terlihat_pengunjung(alamat_uji):
    isi = isi_halaman(alamat_uji, "/tersembunyi/1", "browser")
    assert "display:none" in isi
    assert len(cari_frasa(ekstrak_teks(isi))) >= 3
    assert cari_frasa(ekstrak_teks_terlihat(isi)) == {}


def test_terbuka_judol_terlihat_semua(alamat_uji):
    for persona in PERSONA_SEMUA:
        isi = isi_halaman(alamat_uji, "/terbuka/1", persona)
        assert len(cari_frasa(ekstrak_teks_terlihat(isi))) >= 3


def test_edukasi_hanya_dua_frasa_promosi(alamat_uji):
    isi = isi_halaman(alamat_uji, "/edukasi/1", "browser")
    assert sorted(cari_frasa(ekstrak_teks(isi)).keys()) == ["bonus new member", "slot online"]


def test_dinamis_berubah_antar_kunjungan(alamat_uji):
    isi_a = isi_halaman(alamat_uji, "/dinamis/1", "googlebot")
    isi_b = isi_halaman(alamat_uji, "/dinamis/1", "browser")
    assert isi_a != isi_b


def test_robots_txt_melarang_rahasia(alamat_uji):
    status, lokasi, isi = ambil_mentah(alamat_uji, "/robots.txt", "browser")
    assert status == 200
    assert "Disallow: /rahasia/" in isi
    # Halamannya sendiri tetap ada; yang melarang hanya robots.txt.
    assert ambil_mentah(alamat_uji, "/rahasia/1", "browser")[0] == 200


def test_lambat_melewati_batas_waktu_kecil(alamat_uji):
    with pytest.raises(TimeoutError):
        ambil_mentah(alamat_uji, "/lambat/1", "browser", timeout=1)


def test_semua_link_judol_berakhiran_invalid(alamat_uji):
    jalur_judol = ["/cloak-ua/1", "/cloak-samaran/1", "/tersembunyi/1", "/terbuka/1"]
    for jalur in jalur_judol:
        isi = isi_halaman(alamat_uji, jalur, "googlebot")
        for href in re.findall(r'href="([^"]+)"', isi):
            host = urlsplit(href).hostname
            assert host.endswith(".invalid"), jalur + " -> " + href


def test_alamat_uji_hanya_di_127_0_0_1(alamat_uji):
    assert urlsplit(alamat_uji).hostname == "127.0.0.1"

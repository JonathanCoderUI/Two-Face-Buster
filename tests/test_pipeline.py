"""Tes alur penuh di situs uji: scan, nilai, lalu cek label tiap halaman."""

# File BERSAMA.

import pytest


def jalankan(alamat_uji, tmp_path, daftar_jalur):
    """Scan beberapa halaman situs uji ke database sementara, nilai, lalu kembalikan {jalur: label}."""
    # TODO 1
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_halaman_siluman_tertangkap(alamat_uji, tmp_path):
    # TODO 2:
    # /cloak-ua/1, /cloak-samaran/1, /cloak-referer/1, /tersembunyi/1 harus hampir_pasti.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_halaman_jujur_aman(alamat_uji, tmp_path):
    # TODO 3:
    # /normal/1, /dinamis/1, /edukasi/1 harus aman.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_judol_terbuka_perlu_dicek(alamat_uji, tmp_path):
    # TODO 4:
    # /terbuka/1 harus perlu_dicek.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_robots_txt_dihormati(alamat_uji, tmp_path):
    # TODO 5:
    # /rahasia/1 dilarang robots.txt, jadi labelnya tidak_bisa_dicek.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_redirect_ke_situs_lain_tidak_diikuti(alamat_uji, tmp_path):
    # TODO 6:
    # /cloak-referer/1 untuk persona dari_google: redirect_ke terisi, html None.
    ...

"""Tes untuk skor.py."""

# Pemilik: Detektif.

import pytest


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_skor_halaman_situs_uji(alamat_uji):
    # TODO 1:
    # /cloak-ua/ 70, /cloak-samaran/ 70, /cloak-referer/ 65, /tersembunyi/ 60,
    # /terbuka/ 50, /normal/ 0, /dinamis/ 0, /edukasi/ 0.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_tidak_bisa_dicek_saat_versi_gagal():
    # TODO 2: versi browser atau Googlebot tanpa HTML -> tidak_bisa_dicek, tidak pernah aman.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_artikel_edukasi_aman(alamat_uji):
    # TODO 3: /edukasi/1 berlabel aman.
    ...

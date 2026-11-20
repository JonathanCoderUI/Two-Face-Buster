"""Tes untuk fitur.py."""

# Pemilik: Detektif.

import pytest


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_kemiripan_teks_identik():
    # TODO 1: dua teks yang sama persis bernilai 1.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_kemiripan_situs_uji(alamat_uji):
    # TODO 2: /cloak-ua/1 sekitar 0,37 dan /dinamis/1 sekitar 0,85.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_ekstrak_teks_ambil_meta_buang_script():
    # TODO 3: meta description ikut terambil, isi script dan style tidak.
    ...


@pytest.mark.skip(reason="TODO: Minggu 2")
def test_teks_tersembunyi_tertangkap():
    # TODO 4: blok display:none berisi frasa promosi tertangkap.
    ...


@pytest.mark.skip(reason="TODO: Minggu 2")
def test_menu_tersembunyi_biasa_diabaikan():
    # TODO 5: menu dropdown tersembunyi tanpa frasa promosi dan link luar tidak dilaporkan.
    ...


@pytest.mark.skip(reason="TODO: Minggu 2")
def test_skrip_pengalih_tertangkap():
    # TODO 6: skrip yang membaca document.referrer lalu memindahkan halaman tertangkap.
    ...

"""Tes untuk crawler.py."""

# Pemilik: Penjelajah.

import pytest


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_host_dari():
    # TODO 1:
    # "https://www.Sekolah.sch.id/berita" -> "sekolah.sch.id"; URL rusak -> "".
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_situs_sama():
    # TODO 2:
    # Host yang sama dan subdomainnya True; host berbeda atau kosong False.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_server_mati_dicatat():
    # TODO 3:
    # Kunjungan ke server yang mati tidak membuat crash; galatnya ada di kolom catatan.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_server_lambat_timeout(alamat_uji):
    # TODO 4:
    # /lambat/1 dengan batas waktu kecil dicatat "timeout".
    ...

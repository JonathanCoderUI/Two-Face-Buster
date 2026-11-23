"""Tes untuk fitur.py."""

# Pemilik: Detektif.

import pytest

from siluman.fitur import ekstrak_teks, kemiripan


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


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_kemiripan_situs_uji(alamat_uji):
    # TODO 2: /cloak-ua/1 sekitar 0,37 dan /dinamis/1 sekitar 0,85.
    ...


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

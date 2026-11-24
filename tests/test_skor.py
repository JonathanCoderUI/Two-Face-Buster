"""Tes untuk skor.py."""

# Pemilik: Detektif.

import pytest

from siluman.skor import nilai_url

HTML_SEKOLAH = (
    "<html><head><title>SMA Contoh</title></head><body>"
    "<h1>Berita Sekolah</h1><p>Upacara bendera hari Senin diikuti seluruh siswa dan guru. "
    "Kepala sekolah mengumumkan jadwal ujian akhir semester serta kegiatan ekstrakurikuler "
    "pramuka, basket, dan paduan suara yang dimulai minggu depan di aula sekolah.</p>"
    "</body></html>"
)

HTML_JUDOL = (
    "<html><head><title>SLOT GACOR MAXWIN</title></head><body>"
    "<p>Situs slot gacor hari ini, RTP live tertinggi, pola gacor anti rungkad, "
    "bonus new member 100%, deposit pulsa tanpa potongan.</p></body></html>"
)


def buat_kunjungan(persona, html, status=200, redirect_ke=None, catatan=None):
    """Kembalikan dict kunjungan buatan tangan dengan kolom tabel kunjungan."""
    return {
        "putaran": 1,
        "url": "https://sma-contoh.sch.id/",
        "domain": "sma-contoh.sch.id",
        "persona": persona,
        "waktu": "2026-11-24T10:00:00",
        "status": status,
        "url_akhir": "https://sma-contoh.sch.id/",
        "redirect_ke": redirect_ke,
        "html": html,
        "catatan": catatan,
    }


def buat_versi(html_browser, html_googlebot, html_dari_google):
    """Kembalikan dict versi seperti hasil db.ambil_versi."""
    return {
        "browser": buat_kunjungan("browser", html_browser),
        "googlebot": buat_kunjungan("googlebot", html_googlebot),
        "dari_google": buat_kunjungan("dari_google", html_dari_google),
    }


def test_judol_hanya_untuk_googlebot_seperti_cloak_ua():
    hasil = nilai_url(buat_versi(HTML_SEKOLAH, HTML_JUDOL, HTML_SEKOLAH))
    assert hasil["skor"] == 70
    assert hasil["label"] == "hampir_pasti"
    poin = []
    for alasan in hasil["alasan"]:
        poin.append(alasan["poin"])
    assert sorted(poin) == [20, 50]
    assert hasil["kemiripan"] < 0.5


def test_judol_hanya_untuk_pengunjung_dari_google():
    hasil = nilai_url(buat_versi(HTML_SEKOLAH, HTML_SEKOLAH, HTML_JUDOL))
    assert hasil["skor"] == 50
    assert hasil["label"] == "perlu_dicek"


def test_judol_terbuka_untuk_semua():
    hasil = nilai_url(buat_versi(HTML_JUDOL, HTML_JUDOL, HTML_JUDOL))
    assert hasil["skor"] == 50
    assert hasil["label"] == "perlu_dicek"
    assert hasil["alasan"][0]["teks"] == "Isi judol terlihat oleh semua pengunjung"


def test_halaman_normal_aman():
    hasil = nilai_url(buat_versi(HTML_SEKOLAH, HTML_SEKOLAH, HTML_SEKOLAH))
    assert hasil["skor"] == 0
    assert hasil["label"] == "aman"
    assert hasil["alasan"] == []
    assert hasil["kemiripan"] == 1.0


def test_halaman_dinamis_sedikit_berbeda_aman():
    html_lain = HTML_SEKOLAH.replace("minggu depan", "minggu depan, pukul 07.00 WIB, jangan terlambat")
    hasil = nilai_url(buat_versi(HTML_SEKOLAH, html_lain, HTML_SEKOLAH))
    assert hasil["label"] == "aman"
    assert hasil["kemiripan"] > 0.5


def test_artikel_edukasi_dua_frasa_aman():
    html_edukasi = (
        "<html><body><p>Waspada iklan slot online dan janji bonus new member di media sosial. "
        "Guru BK mengingatkan siswa tentang bahaya judi.</p></body></html>"
    )
    hasil = nilai_url(buat_versi(html_edukasi, html_edukasi, html_edukasi))
    assert hasil["label"] == "aman"


def test_tidak_bisa_dicek_saat_versi_gagal():
    versi = buat_versi(HTML_SEKOLAH, HTML_JUDOL, HTML_SEKOLAH)
    versi["googlebot"] = buat_kunjungan("googlebot", None, status=None, catatan="timeout")
    hasil = nilai_url(versi)
    assert hasil["label"] == "tidak_bisa_dicek"
    assert "timeout" in hasil["alasan"][0]["teks"]

    versi = buat_versi(HTML_SEKOLAH, HTML_JUDOL, HTML_SEKOLAH)
    versi["browser"] = buat_kunjungan("browser", None, status=404)
    assert nilai_url(versi)["label"] == "tidak_bisa_dicek"

    versi = buat_versi(HTML_SEKOLAH, HTML_JUDOL, HTML_SEKOLAH)
    del versi["googlebot"]
    assert nilai_url(versi)["label"] == "tidak_bisa_dicek"


def test_dari_google_gagal_tidak_menggagalkan_penilaian():
    versi = buat_versi(HTML_SEKOLAH, HTML_JUDOL, HTML_SEKOLAH)
    versi["dari_google"] = buat_kunjungan("dari_google", None, status=None, catatan="timeout")
    assert nilai_url(versi)["skor"] == 70


@pytest.mark.skip(reason="TODO: menunggu situs uji dan alamat_uji")
def test_skor_halaman_situs_uji(alamat_uji):
    # TODO 1:
    # /cloak-ua/ 70, /cloak-samaran/ 70, /cloak-referer/ 65, /tersembunyi/ 60,
    # /terbuka/ 50, /normal/ 0, /dinamis/ 0, /edukasi/ 0.
    ...


@pytest.mark.skip(reason="TODO: menunggu situs uji dan alamat_uji")
def test_artikel_edukasi_aman(alamat_uji):
    # TODO 3: /edukasi/1 berlabel aman.
    ...

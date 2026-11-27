"""Tes untuk skor.py."""

# Pemilik: Detektif.

import pytest

import json

from siluman import db
from siluman.skor import nilai_semua, nilai_url
from tests.helper_situs_uji import ambil_versi

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


URL_JUDOL = "https://slot-gacor88.com/daftar"


def html_dengan_tambahan(tambahan):
    """Kembalikan HTML_SEKOLAH dengan HTML tambahan di akhir body."""
    return HTML_SEKOLAH.replace("</body>", tambahan + "</body>")


def test_dari_google_dialihkan_ke_domain_judol_seperti_cloak_referer():
    versi = buat_versi(HTML_SEKOLAH, HTML_SEKOLAH, HTML_SEKOLAH)
    versi["dari_google"] = buat_kunjungan("dari_google", None, status=302, redirect_ke=URL_JUDOL)
    hasil = nilai_url(versi)
    assert hasil["skor"] == 65
    assert hasil["label"] == "hampir_pasti"
    poin = []
    for alasan in hasil["alasan"]:
        poin.append(alasan["poin"])
    assert sorted(poin) == [20, 45]


def test_googlebot_dialihkan_ke_domain_biasa_hanya_poin_pengalihan():
    versi = buat_versi(HTML_SEKOLAH, HTML_SEKOLAH, HTML_SEKOLAH)
    versi["googlebot"] = buat_kunjungan("googlebot", None, status=301, redirect_ke="https://berita-lain.com/")
    hasil = nilai_url(versi)
    assert hasil["skor"] == 45
    assert hasil["label"] == "perlu_dicek"


def test_browser_biasa_dialihkan_ke_domain_judol_terlihat_semua():
    versi = buat_versi(HTML_SEKOLAH, HTML_SEKOLAH, HTML_SEKOLAH)
    versi["browser"] = buat_kunjungan("browser", None, status=302, redirect_ke=URL_JUDOL)
    hasil = nilai_url(versi)
    assert hasil["skor"] == 50
    assert hasil["alasan"][0]["teks"] == "Pengunjung biasa pun dialihkan ke domain berbau judol"


def test_browser_dan_googlebot_sama_sama_dialihkan_bukan_cloaking():
    versi = buat_versi(HTML_SEKOLAH, HTML_SEKOLAH, HTML_SEKOLAH)
    versi["browser"] = buat_kunjungan("browser", HTML_SEKOLAH, status=302, redirect_ke="https://berita-lain.com/")
    versi["googlebot"] = buat_kunjungan("googlebot", None, status=302, redirect_ke="https://berita-lain.com/")
    assert nilai_url(versi)["skor"] == 0


def test_teks_tersembunyi_kuat_seperti_halaman_tersembunyi():
    html = html_dengan_tambahan('<div style="display:none">slot gacor, slot online, bonus new member</div>')
    hasil = nilai_url(buat_versi(html, html, html))
    # Tepat 60, bukan 110: teks tersembunyi tidak ikut dihitung sebagai "isi judol terlihat".
    assert hasil["skor"] == 60
    assert hasil["label"] == "hampir_pasti"
    assert len(hasil["alasan"]) == 1


def test_teks_tersembunyi_lemah_satu_sampai_dua_frasa():
    html = html_dengan_tambahan('<div hidden>slot gacor dan slot online</div>')
    hasil = nilai_url(buat_versi(html, html, html))
    assert hasil["skor"] == 30
    assert hasil["label"] == "perlu_dicek"


def test_menu_tersembunyi_biasa_tetap_aman():
    menu = '<ul style="display:none"><li><a href="/profil">Profil</a></li></ul>'
    html = html_dengan_tambahan(menu)
    hasil = nilai_url(buat_versi(html, html, html))
    assert hasil["skor"] == 0
    assert hasil["label"] == "aman"


def test_skrip_pengalih_menambah_dua_puluh_poin():
    skrip = (
        '<script>if (document.referrer.indexOf("google") > -1) '
        '{ window.location.href = "https://berita-lain.com/"; }</script>'
    )
    html = html_dengan_tambahan(skrip)
    hasil = nilai_url(buat_versi(html, html, html))
    assert hasil["skor"] == 20
    assert hasil["label"] == "aman"
    assert hasil["alasan"][0]["poin"] == 20


def simpan_tiga_versi(conn, url, html_browser, html_googlebot, html_dari_google):
    """Simpan tiga kunjungan buatan tangan untuk satu URL ke database."""
    pasangan = [
        ("browser", html_browser),
        ("googlebot", html_googlebot),
        ("dari_google", html_dari_google),
    ]
    for persona, html in pasangan:
        kunjungan = buat_kunjungan(persona, html)
        kunjungan["url"] = url
        db.simpan_kunjungan(conn, kunjungan)


def test_nilai_semua_menyimpan_hasil_dan_menghitung_per_label():
    conn = db.buka(":memory:")
    simpan_tiga_versi(conn, "https://a.sch.id/", HTML_SEKOLAH, HTML_JUDOL, HTML_SEKOLAH)
    simpan_tiga_versi(conn, "https://b.sch.id/", HTML_SEKOLAH, HTML_SEKOLAH, HTML_SEKOLAH)
    # Hanya versi browser: Googlebot tidak ada, jadi tidak_bisa_dicek.
    kunjungan = buat_kunjungan("browser", HTML_SEKOLAH)
    kunjungan["url"] = "https://c.sch.id/"
    db.simpan_kunjungan(conn, kunjungan)

    jumlah = nilai_semua(conn, 1)

    assert jumlah == {"hampir_pasti": 1, "perlu_dicek": 0, "aman": 1, "tidak_bisa_dicek": 1}
    baris = conn.execute("SELECT * FROM hasil WHERE url = ?", ("https://a.sch.id/",)).fetchone()
    assert baris["skor"] == 70
    assert baris["label"] == "hampir_pasti"
    assert baris["domain"] == "sma-contoh.sch.id"
    assert json.loads(baris["alasan"])[0]["poin"] == 50
    conn.close()


def test_nilai_semua_ulang_tidak_menimpa_verifikasi():
    conn = db.buka(":memory:")
    simpan_tiga_versi(conn, "https://a.sch.id/", HTML_SEKOLAH, HTML_JUDOL, HTML_SEKOLAH)
    nilai_semua(conn, 1)
    db.tandai_verifikasi(conn, 1, "https://a.sch.id/", "benar")
    nilai_semua(conn, 1)
    baris = conn.execute("SELECT verifikasi FROM hasil").fetchone()
    assert baris["verifikasi"] == "benar"
    conn.close()


def test_nilai_semua_putaran_kosong():
    conn = db.buka(":memory:")
    assert nilai_semua(conn, 1) == {"hampir_pasti": 0, "perlu_dicek": 0, "aman": 0, "tidak_bisa_dicek": 0}
    conn.close()


def test_skor_halaman_situs_uji(alamat_uji):
    harapan = {
        "cloak-ua": 70,
        "cloak-samaran": 70,
        "cloak-referer": 65,
        "tersembunyi": 60,
        "terbuka": 50,
        "normal": 0,
        "dinamis": 0,
        "edukasi": 0,
    }
    for nama in harapan:
        versi = ambil_versi(alamat_uji, "/" + nama + "/1")
        assert nilai_url(versi)["skor"] == harapan[nama], nama


def test_artikel_edukasi_aman(alamat_uji):
    hasil = nilai_url(ambil_versi(alamat_uji, "/edukasi/1"))
    assert hasil["label"] == "aman"
    assert abs(hasil["p_judol_browser"] - 2 / 6) < 0.01

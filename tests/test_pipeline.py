"""Tes alur penuh di situs uji: scan, nilai, lalu cek label tiap halaman."""

# File BERSAMA.

import asyncio

from siluman import crawler, db, skor


def jalankan(alamat_uji, tmp_path, daftar_jalur):
    """Scan beberapa halaman situs uji ke database sementara, nilai, lalu kembalikan {jalur: label}."""
    conn = db.buka(str(tmp_path / "pipeline.db"))
    daftar_url = []
    for jalur in daftar_jalur:
        daftar_url.append(alamat_uji + jalur)
    # Jeda 0: situs ini milik kita sendiri, tidak perlu menunggu antar kunjungan.
    asyncio.run(crawler.scan(daftar_url, conn, 1, 0))
    skor.nilai_semua(conn, 1)
    hasil = {}
    for jalur in daftar_jalur:
        baris = conn.execute(
            "SELECT label FROM hasil WHERE putaran = 1 AND url = ?", (alamat_uji + jalur,)
        ).fetchone()
        hasil[jalur] = baris["label"]
    conn.close()
    return hasil


def test_halaman_siluman_tertangkap(alamat_uji, tmp_path):
    jalur_siluman = ["/cloak-ua/1", "/cloak-samaran/1", "/cloak-referer/1", "/tersembunyi/1"]
    hasil = jalankan(alamat_uji, tmp_path, jalur_siluman)
    for jalur in jalur_siluman:
        assert hasil[jalur] == "hampir_pasti", jalur


def test_halaman_jujur_aman(alamat_uji, tmp_path):
    jalur_jujur = ["/normal/1", "/dinamis/1", "/edukasi/1"]
    hasil = jalankan(alamat_uji, tmp_path, jalur_jujur)
    for jalur in jalur_jujur:
        assert hasil[jalur] == "aman", jalur


def test_judol_terbuka_perlu_dicek(alamat_uji, tmp_path):
    hasil = jalankan(alamat_uji, tmp_path, ["/terbuka/1"])
    assert hasil["/terbuka/1"] == "perlu_dicek"


def test_robots_txt_dihormati(alamat_uji, tmp_path):
    hasil = jalankan(alamat_uji, tmp_path, ["/rahasia/1"])
    assert hasil["/rahasia/1"] == "tidak_bisa_dicek"


def test_redirect_ke_situs_lain_tidak_diikuti(alamat_uji, tmp_path):
    conn = db.buka(str(tmp_path / "redirect.db"))
    url = alamat_uji + "/cloak-referer/1"
    asyncio.run(crawler.scan([url], conn, 1, 0))
    versi = db.ambil_versi(conn, 1, url)
    conn.close()
    assert versi["dari_google"]["redirect_ke"] == "http://slot-gacor-uji.invalid/daftar"
    assert versi["dari_google"]["html"] == None
    assert versi["browser"]["redirect_ke"] == None
    assert versi["browser"]["html"] != None

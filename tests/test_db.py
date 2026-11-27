"""Tes untuk db.py."""

# Pemilik: bersama.

import pytest

from siluman import db


@pytest.fixture
def conn():
    koneksi = db.buka(":memory:")
    yield koneksi
    koneksi.close()


def buat_kunjungan(persona, html="<p>halo</p>", putaran=1, url="https://sma-contoh.sch.id/"):
    return {
        "putaran": putaran,
        "url": url,
        "domain": "sma-contoh.sch.id",
        "persona": persona,
        "waktu": "2026-11-27T10:00:00",
        "status": 200,
        "url_akhir": url,
        "redirect_ke": None,
        "html": html,
        "catatan": None,
    }


def buat_hasil(putaran=1, url="https://sma-contoh.sch.id/", skor=70, label="hampir_pasti"):
    return {
        "putaran": putaran,
        "url": url,
        "domain": "sma-contoh.sch.id",
        "skor": skor,
        "label": label,
        "alasan": [{"poin": 50, "teks": "Isi judol hanya muncul untuk Googlebot"}],
        "kemiripan": 0.37,
        "p_judol_browser": 0.0,
        "p_judol_googlebot": 0.83,
        "waktu": "2026-11-27T10:05:00",
    }


def test_buka_membuat_folder_dan_tabel(tmp_path):
    lokasi = str(tmp_path / "data" / "siluman.db")
    koneksi = db.buka(lokasi)
    nama_tabel = []
    for baris in koneksi.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
        nama_tabel.append(baris["name"])
    koneksi.close()
    assert "kunjungan" in nama_tabel
    assert "hasil" in nama_tabel
    assert "laporan" in nama_tabel


def test_html_bolak_balik_lewat_zlib(conn):
    html = "<p>Penerimaan siswa baru — ＳＬＯＴ</p>"
    db.simpan_kunjungan(conn, buat_kunjungan("browser", html))
    versi = db.ambil_versi(conn, 1, "https://sma-contoh.sch.id/")
    assert versi["browser"]["html"] == html
    mentah = conn.execute("SELECT html FROM kunjungan").fetchone()["html"]
    assert mentah != html.encode("utf-8")


def test_html_none_untuk_kunjungan_gagal(conn):
    k = buat_kunjungan("googlebot", None)
    k["status"] = None
    k["catatan"] = "timeout"
    db.simpan_kunjungan(conn, k)
    versi = db.ambil_versi(conn, 1, "https://sma-contoh.sch.id/")
    assert versi["googlebot"]["html"] == None
    assert versi["googlebot"]["catatan"] == "timeout"


def test_persona_tak_ditemukan_bernilai_none(conn):
    db.simpan_kunjungan(conn, buat_kunjungan("browser"))
    versi = db.ambil_versi(conn, 1, "https://sma-contoh.sch.id/")
    assert versi["browser"] != None
    assert versi["googlebot"] == None
    assert versi["dari_google"] == None


def test_url_tak_dikenal_semua_none(conn):
    versi = db.ambil_versi(conn, 1, "https://tidak-ada.sch.id/")
    assert versi == {"browser": None, "googlebot": None, "dari_google": None}


def test_kunjungan_ulang_menggantikan_yang_lama(conn):
    db.simpan_kunjungan(conn, buat_kunjungan("browser", "<p>lama</p>"))
    db.simpan_kunjungan(conn, buat_kunjungan("browser", "<p>baru</p>"))
    versi = db.ambil_versi(conn, 1, "https://sma-contoh.sch.id/")
    assert versi["browser"]["html"] == "<p>baru</p>"


def test_putaran_dipisah(conn):
    db.simpan_kunjungan(conn, buat_kunjungan("browser", "<p>satu</p>", putaran=1))
    db.simpan_kunjungan(conn, buat_kunjungan("browser", "<p>dua</p>", putaran=2))
    assert db.ambil_versi(conn, 1, "https://sma-contoh.sch.id/")["browser"]["html"] == "<p>satu</p>"
    assert db.ambil_versi(conn, 2, "https://sma-contoh.sch.id/")["browser"]["html"] == "<p>dua</p>"


def test_simpan_hasil_menyimpan_alasan_sebagai_json(conn):
    db.simpan_hasil(conn, buat_hasil())
    baris = conn.execute("SELECT * FROM hasil").fetchone()
    assert baris["skor"] == 70
    assert baris["alasan"].startswith("[")
    assert "Googlebot" in baris["alasan"]


def test_simpan_hasil_ulang_tidak_menimpa_verifikasi(conn):
    db.simpan_hasil(conn, buat_hasil(skor=70))
    db.tandai_verifikasi(conn, 1, "https://sma-contoh.sch.id/", "benar")
    db.simpan_hasil(conn, buat_hasil(skor=55, label="perlu_dicek"))
    baris = conn.execute("SELECT * FROM hasil").fetchone()
    assert baris["skor"] == 55
    assert baris["label"] == "perlu_dicek"
    assert baris["verifikasi"] == "benar"


def test_tandai_verifikasi_menolak_nilai_lain(conn):
    db.simpan_hasil(conn, buat_hasil())
    with pytest.raises(ValueError):
        db.tandai_verifikasi(conn, 1, "https://sma-contoh.sch.id/", "mungkin")


def test_catat_laporan_memperbarui_status(conn):
    db.catat_laporan(conn, "sma-contoh.sch.id", "draf", "", "2026-11-27")
    db.catat_laporan(conn, "sma-contoh.sch.id", "terkirim", "dikirim ke admin", "2026-11-28")
    baris_semua = conn.execute("SELECT * FROM laporan").fetchall()
    assert len(baris_semua) == 1
    assert baris_semua[0]["status"] == "terkirim"
    assert baris_semua[0]["tanggal"] == "2026-11-28"


def test_catat_laporan_menolak_status_asing(conn):
    with pytest.raises(ValueError):
        db.catat_laporan(conn, "sma-contoh.sch.id", "selesai", "", "2026-11-27")


def test_url_dicurigai_hanya_dua_label(conn):
    db.simpan_hasil(conn, buat_hasil(url="https://a.sch.id/", skor=70, label="hampir_pasti"))
    db.simpan_hasil(conn, buat_hasil(url="https://b.sch.id/", skor=40, label="perlu_dicek"))
    db.simpan_hasil(conn, buat_hasil(url="https://c.sch.id/", skor=0, label="aman"))
    db.simpan_hasil(conn, buat_hasil(url="https://d.sch.id/", skor=0, label="tidak_bisa_dicek"))
    db.simpan_hasil(conn, buat_hasil(putaran=2, url="https://e.sch.id/", skor=70))
    assert db.url_dicurigai(conn, 1) == ["https://a.sch.id/", "https://b.sch.id/"]


def test_daftar_url_tanpa_duplikat(conn):
    for persona in ["browser", "googlebot", "dari_google"]:
        db.simpan_kunjungan(conn, buat_kunjungan(persona, url="https://a.sch.id/"))
    db.simpan_kunjungan(conn, buat_kunjungan("browser", url="https://b.sch.id/"))
    db.simpan_kunjungan(conn, buat_kunjungan("browser", putaran=2, url="https://c.sch.id/"))
    assert db.daftar_url(conn, 1) == ["https://a.sch.id/", "https://b.sch.id/"]


def test_nama_folder_aman():
    assert db.nama_folder("https://sma-contoh.sch.id/berita/1") == "sma-contoh.sch.id_berita_1"
    assert db.nama_folder("https://sma-contoh.sch.id/") == "sma-contoh.sch.id"
    assert db.nama_folder("http://x.sch.id/../../etc/passwd") == "x.sch.id_.._.._etc_passwd"


def test_nama_folder_tanpa_pemisah_path_berbahaya():
    nama = db.nama_folder("https://x.sch.id/a/b?c=d&e=f#g")
    assert "/" not in nama
    assert "\\" not in nama
    assert "?" not in nama


def test_nama_folder_kosong_atau_rusak():
    assert db.nama_folder("") == "tanpa_nama"
    assert db.nama_folder("bukan url") == "bukan_url"


def test_nama_folder_dipotong_kalau_terlalu_panjang():
    url = "https://x.sch.id/" + "a" * 500
    assert len(db.nama_folder(url)) <= 100

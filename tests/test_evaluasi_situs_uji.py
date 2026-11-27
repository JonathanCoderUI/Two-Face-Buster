"""Tes untuk perhitungan precision dan recall di scripts/evaluasi_situs_uji.py."""

# Pemilik: Detektif.

from scripts import evaluasi_situs_uji as evaluasi
from siluman import db


def test_hitung_matriks_empat_kemungkinan():
    pasangan = [
        (True, True),
        (True, True),
        (True, False),
        (False, True),
        (False, False),
        (False, False),
        (False, False),
    ]
    assert evaluasi.hitung_matriks(pasangan) == {"tp": 2, "fp": 1, "fn": 1, "tn": 3}


def test_precision_dan_recall():
    matriks = {"tp": 8, "fp": 2, "fn": 2, "tn": 8}
    assert abs(evaluasi.hitung_precision(matriks) - 0.8) < 0.001
    assert abs(evaluasi.hitung_recall(matriks) - 0.8) < 0.001
    matriks = {"tp": 3, "fp": 0, "fn": 1, "tn": 10}
    assert evaluasi.hitung_precision(matriks) == 1.0
    assert abs(evaluasi.hitung_recall(matriks) - 0.75) < 0.001


def test_pembagi_nol_tidak_error():
    tidak_ada_yang_ditandai = {"tp": 0, "fp": 0, "fn": 5, "tn": 5}
    assert evaluasi.hitung_precision(tidak_ada_yang_ditandai) == None
    assert evaluasi.hitung_recall(tidak_ada_yang_ditandai) == 0.0
    tidak_ada_yang_bertrik = {"tp": 0, "fp": 1, "fn": 0, "tn": 5}
    assert evaluasi.hitung_recall(tidak_ada_yang_bertrik) == None
    assert evaluasi.format_persen(None) == "tidak terdefinisi"
    assert evaluasi.format_persen(0.8) == "80.0%"


def test_label_ditandai():
    assert evaluasi.label_ditandai("hampir_pasti") == True
    assert evaluasi.label_ditandai("perlu_dicek") == True
    assert evaluasi.label_ditandai("aman") == False
    # Tidak bisa dicek tidak dihitung sebagai ditandai, jadi halaman bertrik yang gagal diambil menjadi FN.
    assert evaluasi.label_ditandai("tidak_bisa_dicek") == False


def test_buat_daftar_alamat():
    daftar = evaluasi.buat_daftar_alamat({"cloak-ua": 2, "normal": 1})
    assert daftar == [
        "http://127.0.0.1:5050/cloak-ua/1",
        "http://127.0.0.1:5050/cloak-ua/2",
        "http://127.0.0.1:5050/normal/1",
    ]


def test_jumlah_halaman_sesuai_spesifikasi():
    assert len(evaluasi.buat_daftar_alamat(evaluasi.HALAMAN_BERTRIK)) == 30
    assert len(evaluasi.buat_daftar_alamat(evaluasi.HALAMAN_JUJUR)) == 30


def test_kumpulkan_pasangan_dari_database():
    conn = db.buka(":memory:")
    url_trik = "http://127.0.0.1:5050/cloak-ua/1"
    url_jujur = "http://127.0.0.1:5050/normal/1"
    url_hilang = "http://127.0.0.1:5050/normal/2"
    db.simpan_hasil(conn, {"putaran": 1, "url": url_trik, "skor": 70, "label": "hampir_pasti", "alasan": []})
    db.simpan_hasil(conn, {"putaran": 1, "url": url_jujur, "skor": 0, "label": "aman", "alasan": []})
    pasangan, tanpa_hasil = evaluasi.kumpulkan_pasangan(conn, [url_trik], [url_jujur, url_hilang])
    assert pasangan == [(True, True), (False, False)]
    assert tanpa_hasil == [url_hilang]
    conn.close()

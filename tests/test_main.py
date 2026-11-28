"""Tes untuk main.py: perintah terminal harus menyambung ke modul yang benar."""

# File BERSAMA.

import csv

import pytest

import main
from siluman import db


def tulis_csv_url(lokasi, daftar_url, ada_judul=True):
    """Tulis CSV berkolom url, boleh dengan baris kosong di tengah."""
    with open(lokasi, "w", newline="", encoding="utf-8") as berkas:
        penulis = csv.writer(berkas)
        if ada_judul:
            penulis.writerow(["url"])
        for url in daftar_url:
            penulis.writerow([url])


def test_baca_url_melewati_baris_kosong(tmp_path):
    lokasi = str(tmp_path / "url.csv")
    tulis_csv_url(lokasi, ["http://a.sch.id/", "", "http://b.sch.id/", "  "])
    assert main.baca_url(lokasi) == ["http://a.sch.id/", "http://b.sch.id/"]


def test_baca_url_file_tidak_ada(tmp_path):
    with pytest.raises(FileNotFoundError):
        main.baca_url(str(tmp_path / "tidak-ada.csv"))


def jalankan_main(*argumen):
    """Jalankan main() dengan daftar argumen, seperti mengetik di terminal."""
    main.main(list(argumen))


def test_scan_lalu_nilai_lewat_terminal(alamat_uji, tmp_path, capsys):
    lokasi_db = str(tmp_path / "siluman.db")
    lokasi_csv = str(tmp_path / "url.csv")
    tulis_csv_url(lokasi_csv, [alamat_uji + "/cloak-ua/1", alamat_uji + "/normal/1"])

    jalankan_main("--db", lokasi_db, "--putaran", "3", "scan", "--input", lokasi_csv, "--jeda", "0")
    jalankan_main("--db", lokasi_db, "--putaran", "3", "nilai")

    conn = db.buka(lokasi_db)
    baris_semua = conn.execute("SELECT url, label FROM hasil WHERE putaran = 3").fetchall()
    conn.close()
    label = {}
    for baris in baris_semua:
        label[baris["url"]] = baris["label"]
    assert label[alamat_uji + "/cloak-ua/1"] == "hampir_pasti"
    assert label[alamat_uji + "/normal/1"] == "aman"
    # Ringkasan jumlah per label dicetak untuk pengguna.
    keluaran = capsys.readouterr().out
    assert "hampir_pasti" in keluaran


def test_putaran_terpisah(alamat_uji, tmp_path):
    lokasi_db = str(tmp_path / "siluman.db")
    lokasi_csv = str(tmp_path / "url.csv")
    tulis_csv_url(lokasi_csv, [alamat_uji + "/normal/1"])
    jalankan_main("--db", lokasi_db, "--putaran", "1", "scan", "--input", lokasi_csv, "--jeda", "0")
    jalankan_main("--db", lokasi_db, "--putaran", "2", "scan", "--input", lokasi_csv, "--jeda", "0")
    conn = db.buka(lokasi_db)
    assert db.daftar_url(conn, 1) == [alamat_uji + "/normal/1"]
    assert db.daftar_url(conn, 2) == [alamat_uji + "/normal/1"]
    conn.close()


def test_file_input_tidak_ada_berhenti_dengan_pesan(tmp_path, capsys):
    with pytest.raises(SystemExit) as galat:
        jalankan_main("--db", str(tmp_path / "x.db"), "scan", "--input", str(tmp_path / "hilang.csv"))
    assert galat.value.code == 1
    assert "hilang.csv" in capsys.readouterr().err


def test_ekspor_label_lewat_terminal(alamat_uji, tmp_path):
    lokasi_db = str(tmp_path / "siluman.db")
    lokasi_csv = str(tmp_path / "url.csv")
    lokasi_label = str(tmp_path / "label.csv")
    tulis_csv_url(lokasi_csv, [alamat_uji + "/cloak-ua/1", alamat_uji + "/normal/1"])
    jalankan_main("--db", lokasi_db, "scan", "--input", lokasi_csv, "--jeda", "0")
    jalankan_main("--db", lokasi_db, "nilai")
    jalankan_main("--db", lokasi_db, "ekspor-label", "--keluar", lokasi_label)
    with open(lokasi_label, newline="", encoding="utf-8-sig") as berkas:
        baris_semua = list(csv.DictReader(berkas))
    assert len(baris_semua) >= 2


def test_subperintah_wajib():
    with pytest.raises(SystemExit):
        jalankan_main()

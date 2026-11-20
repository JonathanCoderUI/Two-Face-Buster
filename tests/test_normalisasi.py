"""Tes untuk normalisasi.py."""

# Pemilik: Detektif.

from siluman.normalisasi import cari_frasa, nilai_judol_kata_kunci, normalisasi

# Karakter tak terlihat dan huruf Kiril ditulis sebagai kode escape, bukan ditempel
# langsung, supaya reviewer bisa melihat bahwa karakternya memang berbeda.
SPASI_LEBAR_NOL = "​"
O_KIRIL = "о"


def test_angka_mirip_huruf():
    assert normalisasi("S1OT G4C0R") == "siot gacor"


def test_karakter_tak_terlihat():
    assert normalisasi("sl" + SPASI_LEBAR_NOL + "ot") == "siot"


def test_huruf_lebar():
    assert normalisasi("ＳＬＯＴ") == "siot"


def test_huruf_kiril():
    assert normalisasi("sl" + O_KIRIL + "t") == "siot"


def test_huruf_berulang():
    assert normalisasi("gacooor") == "gacor"


def test_maxwin_samaran():
    assert normalisasi("M4XW1N") == "maxwin"


def test_frasa_digabung_dan_tanda_hubung():
    assert "slot gacor" in cari_frasa("promo slotgacor hari ini")
    assert "slot gacor" in cari_frasa("promo slot-gacor hari ini")


def test_slot_pendaftaran_tidak_terpicu():
    assert cari_frasa("Jadwal slot pendaftaran PPDB sudah dibuka") == {}


def test_artikel_edukasi_di_bawah_ambang():
    teks = "Waspada iklan slot online dan janji bonus new member di media sosial."
    nilai = nilai_judol_kata_kunci(teks)
    assert abs(nilai - 2 / 6) < 0.01
    assert nilai < 0.5

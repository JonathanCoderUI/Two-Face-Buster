"""Tes untuk normalisasi.py."""

# Pemilik: Detektif. Tulis tesnya dulu, lihat gagal, baru buat lulus.

import pytest


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_angka_mirip_huruf():
    # TODO 1: "S1OT G4C0R" -> "siot gacor"
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_karakter_tak_terlihat():
    # TODO 2: "sl" + U+200B + "ot" -> "siot"
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_huruf_lebar():
    # TODO 3: "SLOT" ditulis dengan huruf lebar -> "siot"
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_huruf_kiril():
    # TODO 4: "slot" dengan huruf o Kiril -> "siot"
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_huruf_berulang():
    # TODO 5: "gacooor" -> "gacor"
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_maxwin_samaran():
    # TODO 6: "M4XW1N" -> "maxwin"
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_frasa_digabung_dan_tanda_hubung():
    # TODO 7: "slotgacor" dan "slot-gacor" tetap cocok dengan frasa "slot gacor".
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_slot_pendaftaran_tidak_terpicu():
    # TODO 8: "slot pendaftaran PPDB" tidak cocok dengan frasa promosi mana pun.
    ...


@pytest.mark.skip(reason="TODO: belum ditulis")
def test_artikel_edukasi_di_bawah_ambang():
    # TODO 9: teks dengan 2 frasa promosi bernilai sekitar 0,33, di bawah 0,5.
    ...

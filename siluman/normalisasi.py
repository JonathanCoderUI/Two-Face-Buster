"""Melipat ejaan samaran ke satu bentuk dan mencari frasa promosi judi."""

# Pemilik: Detektif.

import re
import unicodedata

# Angka yang mirip huruf, huruf l yang mirip i, dan huruf Kiril yang mirip huruf Latin.
# "l" ikut dipetakan ke "i" karena "1" dan "l" sama-sama dipakai menyamarkan "i" dan "l";
# hasilnya "slot" menjadi "siot", tidak masalah karena teks dan frasa dilipat sama.
PETA_HURUF_MIRIP = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "l": "i",
    "а": "a",  # Kiril
    "в": "b",
    "е": "e",
    "к": "k",
    "м": "m",
    "н": "h",
    "о": "o",
    "р": "p",
    "с": "c",
    "т": "t",
    "у": "y",
    "х": "x",
    "і": "i",
    "ј": "j",
    "ѕ": "s",
}

# Frasa, bukan kata tunggal, supaya "slot pendaftaran PPDB" tidak terpicu.
FRASA_PROMOSI = [
    "slot gacor",
    "slot online",
    "slot maxwin",
    "situs slot",
    "situs gacor",
    "link slot",
    "daftar slot",
    "agen slot",
    "bocoran slot",
    "pola gacor",
    "rtp live",
    "bonus new member",
    "deposit pulsa",
    "gampang menang",
    "anti rungkad",
    "scatter hitam",
    "bandar togel",
    "togel online",
]

# Nilai judol mencapai 1 saat ada sebanyak ini frasa berbeda (spesifikasi skor).
PEMBAGI_FRASA = 6

KATEGORI_DIBUANG = ["Mn", "Cf"]


def normalisasi(teks):
    """Kembalikan teks yang ejaan samarannya sudah dilipat ke satu bentuk."""
    if teks == None:
        return ""
    teks = unicodedata.normalize("NFKD", teks)
    teks = buang_kategori(teks)
    teks = teks.lower()
    teks = ganti_huruf_mirip(teks)
    teks = rapikan_spasi(teks)
    teks = rapatkan_huruf_berulang(teks)
    return teks


def buang_kategori(teks):
    """Kembalikan teks tanpa tanda diakritik (Mn) dan karakter tak terlihat (Cf)."""
    hasil = ""
    for c in teks:
        if unicodedata.category(c) in KATEGORI_DIBUANG:
            continue
        hasil = hasil + c
    return hasil


def ganti_huruf_mirip(teks):
    """Kembalikan teks dengan setiap huruf mirip diganti huruf Latin pasangannya."""
    hasil = ""
    for c in teks:
        if c in PETA_HURUF_MIRIP:
            hasil = hasil + PETA_HURUF_MIRIP[c]
        else:
            hasil = hasil + c
    return hasil


def rapikan_spasi(teks):
    """Kembalikan teks dengan deretan spasi, tab, atau baris baru dijadikan satu spasi."""
    potongan = teks.split()
    return " ".join(potongan)


def rapatkan_huruf_berulang(teks):
    """Kembalikan teks dengan deretan karakter yang sama dijadikan satu karakter."""
    hasil = ""
    sebelumnya = None
    for c in teks:
        if c == sebelumnya:
            continue
        hasil = hasil + c
        sebelumnya = c
    return hasil


def pola_frasa(frasa):
    """Kembalikan regex yang cocok dengan frasa walau kata-katanya digabung atau diberi tanda hubung."""
    kata_kata = normalisasi(frasa).split(" ")
    bagian = []
    for kata in kata_kata:
        bagian.append(re.escape(kata))
    # Pemisah antarkata boleh kosong ("slotgacor") atau tanda baca apa pun ("slot-gacor").
    return re.compile("[^a-z0-9]*".join(bagian))


def cari_frasa(teks):
    """Kembalikan {frasa: jumlah kemunculan} untuk setiap frasa promosi di teks."""
    teks_lipat = normalisasi(teks)
    ditemukan = {}
    for frasa in FRASA_PROMOSI:
        jumlah = len(pola_frasa(frasa).findall(teks_lipat))
        if jumlah > 0:
            ditemukan[frasa] = jumlah
    return ditemukan


def nilai_judol_kata_kunci(teks):
    """Kembalikan nilai 0 sampai 1: banyaknya frasa berbeda dibagi 6, maksimal 1."""
    nilai = len(cari_frasa(teks)) / PEMBAGI_FRASA
    if nilai > 1:
        return 1.0
    else:
        return nilai

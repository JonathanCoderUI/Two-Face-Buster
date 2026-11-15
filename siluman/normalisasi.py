"""Melipat ejaan samaran ke satu bentuk dan mencari frasa promosi judi."""

# Pemilik: Detektif.

# TODO 1:
# Peta huruf mirip: angka yang mirip huruf dan huruf Kiril yang mirip huruf Latin.
PETA_HURUF_MIRIP = ...

# TODO 2:
# Daftar frasa promosi judol. Frasa, bukan kata tunggal seperti "slot".
FRASA_PROMOSI = ...


def normalisasi(teks):
    """Kembalikan teks yang ejaan samarannya sudah dilipat ke satu bentuk."""
    # TODO 3:
    # Ikuti 6 langkah spesifikasi: NFKD, buang kategori Mn dan Cf, huruf kecil,
    # peta huruf mirip, rapikan spasi, rapatkan huruf berulang.
    # Cocokkan hasilnya dengan tabel Masukan -> Hasil di spesifikasi.
    ...


def cari_frasa(teks):
    """Kembalikan {frasa: jumlah kemunculan} untuk setiap frasa promosi di teks."""
    # TODO 4:
    # Teks dan frasa dilipat dengan normalisasi yang sama.
    # Harus cocok untuk "slotgacor" dan "slot-gacor", tapi tidak untuk "slot pendaftaran PPDB".
    ...


def nilai_judol_kata_kunci(teks):
    """Kembalikan nilai 0 sampai 1: banyaknya frasa berbeda dibagi 6, maksimal 1."""
    # TODO 5
    ...

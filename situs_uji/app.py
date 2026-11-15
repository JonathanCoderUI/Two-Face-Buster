"""Situs tiruan di 127.0.0.1 yang sengaja berperilaku seperti situs siluman."""

# Pemilik: Pelapor. Rujukan: Panduan hlm. 12-16.
# Aturan situs uji: hanya jalan di 127.0.0.1, semua isi judol bertanda CONTOH UJI,
# semua link judol berakhiran .invalid.

# TODO 1:
# Buat aplikasi Flask, teks sambutan sekolah, daftar pengumuman, dan teks judol contoh.
...


def halaman(judul, isi, n, tambahan=""):
    """Kembalikan HTML halaman sekolah dengan judul, isi, dan pengumuman ke-n."""
    # TODO 2
    ...


def dari_googlebot():
    """True kalau User-Agent permintaan memuat googlebot."""
    # TODO 3
    ...


def dari_google():
    """True kalau Referer permintaan berasal dari Google."""
    # TODO 4
    ...


# TODO 5:
# Satu route untuk tiap jalur, perilaku dan label yang diharapkan ada di Panduan hlm. 12-13:
# /normal/<n>, /dinamis/<n>, /edukasi/<n>, /cloak-ua/<n>, /cloak-samaran/<n>,
# /cloak-referer/<n>, /tersembunyi/<n>, /terbuka/<n>, /rahasia/<n>, /lambat/<n>, /robots.txt


def jalankan_di_latar():
    """Jalankan situs uji di thread terpisah pada port acak, lalu kembalikan (server, alamat)."""
    # TODO 6:
    # Dipakai fixture alamat_uji di tests/conftest.py.
    ...


if __name__ == "__main__":
    # TODO 7:
    # Jalankan di 127.0.0.1 port 5050.
    ...

"""Mengambil tanda-tanda dari HTML untuk dinilai skor.py."""

# Pemilik: Detektif.


def ekstrak_teks(html):
    """Kembalikan teks yang dibaca mesin pencari: isi halaman, judul, dan meta description."""
    # TODO 1 (Minggu 1):
    # Isi script dan style dibuang, spasi dan baris baru dirapikan.
    # Dipakai juga oleh dashboard.py.
    ...


def kemiripan(teks_a, teks_b):
    """Kembalikan 0 sampai 1: seberapa mirip urutan kata dua teks (1 = identik)."""
    # TODO 2 (Minggu 1):
    # Pakai difflib atas daftar kata, bukan atas huruf.
    # Di situs uji: /cloak-ua/ sekitar 0,37 dan /dinamis/ sekitar 0,85.
    ...


def cari_teks_tersembunyi(html, url):
    """Kembalikan daftar elemen tersembunyi yang berisi frasa promosi atau banyak link ke situs lain."""
    # TODO 3 (Minggu 2):
    # Tersembunyi: atribut hidden, display:none, visibility:hidden, font-size:0,
    # opacity:0, atau digeser jauh keluar layar.
    # Dilaporkan kalau berisi frasa promosi atau minimal 3 link ke situs lain.
    ...


def skrip_pengalih_referrer(html):
    """True kalau ada skrip yang memeriksa asal kunjungan, menyebut google, lalu memindahkan halaman."""
    # TODO 4 (Minggu 2)
    ...


def nama_domain_berbau_judol(url):
    """True kalau nama domain URL mengandung kata berbau judol seperti slot atau gacor."""
    # TODO 5 (Minggu 2)
    ...

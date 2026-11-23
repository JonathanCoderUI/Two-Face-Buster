"""Mengambil tanda-tanda dari HTML untuk dinilai skor.py."""

# Pemilik: Detektif.

import difflib

from bs4 import BeautifulSoup

from siluman.normalisasi import rapikan_spasi

# Isinya kode, bukan teks yang dibaca pengunjung atau mesin pencari.
TAG_DIBUANG = ["script", "style"]


def ekstrak_teks(html):
    """Kembalikan teks yang dibaca mesin pencari: isi halaman, judul, dan meta description."""
    if html == None or html == "":
        return ""
    soup = BeautifulSoup(html, "html.parser")

    judul = ambil_judul(soup)
    deskripsi = ambil_meta_description(soup)

    for nama_tag in TAG_DIBUANG:
        for tag in soup.find_all(nama_tag):
            tag.decompose()
    # Judul sudah diambil di atas; dibuang supaya tidak terhitung dua kali di isi.
    if soup.title != None:
        soup.title.decompose()
    isi = soup.get_text(" ")

    return rapikan_spasi(judul + " " + deskripsi + " " + isi)


def ambil_judul(soup):
    """Kembalikan teks tag title, atau "" kalau tidak ada."""
    if soup.title == None:
        return ""
    else:
        return soup.title.get_text(" ")


def ambil_meta_description(soup):
    """Kembalikan isi atribut content dari meta description, atau "" kalau tidak ada."""
    for meta in soup.find_all("meta"):
        nama = meta.get("name")
        if nama != None and nama.lower() == "description":
            isi = meta.get("content")
            if isi == None:
                return ""
            else:
                return isi
    return ""


def kemiripan(teks_a, teks_b):
    """Kembalikan 0 sampai 1: seberapa mirip urutan kata dua teks (1 = identik)."""
    # Dibandingkan per kata, bukan per huruf: halaman sekolah dan halaman judol
    # sama-sama penuh huruf a, n, dan spasi, jadi per huruf selalu tampak mirip.
    # Dua teks kosong bernilai 1; kasus "isi tidak bisa dibandingkan" diurus skor.py.
    kata_a = teks_a.split()
    kata_b = teks_b.split()
    return difflib.SequenceMatcher(None, kata_a, kata_b).ratio()


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

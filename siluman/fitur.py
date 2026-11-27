"""Mengambil tanda-tanda dari HTML untuk dinilai skor.py."""

# Pemilik: Detektif.

import difflib
import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from siluman.crawler import host_dari, situs_sama
from siluman.normalisasi import cari_frasa, normalisasi, rapikan_spasi

# Isinya kode, bukan teks yang dibaca pengunjung atau mesin pencari.
TAG_DIBUANG = ["script", "style"]

# Kata yang hampir selalu berarti judi kalau muncul di nama domain.
# Kata pendek seperti "bet" sengaja tidak dimasukkan karena sering muncul di
# kata biasa (misalnya alphabet).
KATA_DOMAIN_JUDOL = [
    "slot",
    "gacor",
    "maxwin",
    "togel",
    "judi",
    "casino",
    "kasino",
    "poker",
    "jackpot",
    "scatter",
]

# ---- Teks tersembunyi ----
MIN_LINK_LUAR_TERSEMBUNYI = 3   # elemen tersembunyi dengan link luar sebanyak ini dilaporkan
BATAS_GESER_KELUAR_LAYAR = 500  # geser negatif sejauh ini (px) dianggap di luar layar
PANJANG_CUPLIKAN = 80
PROPERTI_GESER = ["left", "right", "top", "bottom", "text-indent", "margin-left"]
POLA_NOL = re.compile(r"^0(\.0+)?(px|pt|em|rem|%)?$")
POLA_GESER_NEGATIF = re.compile(r"^-(\d+(\.\d+)?)")

# ---- Skrip pengalih ----
# Mencocokkan pemindahan halaman: location = ..., location.href = ..., location.replace(...).
# "==" sengaja dikecualikan karena itu perbandingan, bukan pemindahan.
POLA_PINDAH_HALAMAN = re.compile(r"location(\.href)?\s*=[^=]|location\.(replace|assign)\s*\(")


def ekstrak_teks(html):
    """Kembalikan teks yang dibaca mesin pencari: isi halaman, judul, dan meta description."""
    return ambil_teks(html, False)


def ekstrak_teks_terlihat(html):
    """Seperti ekstrak_teks, tapi tanpa elemen tersembunyi: teks yang benar-benar dilihat pengunjung."""
    return ambil_teks(html, True)


def ambil_teks(html, buang_tersembunyi):
    """Kembalikan judul, meta description, dan isi halaman; elemen tersembunyi dibuang kalau diminta."""
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
    if buang_tersembunyi:
        # Hanya yang terluar: membuang anak setelah induknya dibuang akan error.
        for tag in cari_tag_tersembunyi_terluar(soup):
            tag.decompose()
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
    # Hanya atribut hidden dan style inline yang dibaca. Elemen yang disembunyikan lewat
    # class atau stylesheet terpisah tidak terdeteksi karena CSS-nya tidak dijalankan.
    temuan = []
    if html == None or html == "":
        return temuan
    soup = BeautifulSoup(html, "html.parser")

    for tag in cari_tag_tersembunyi_terluar(soup):
        teks = rapikan_spasi(tag.get_text(" "))
        frasa = sorted(cari_frasa(teks).keys())
        jumlah_link = hitung_link_luar(tag, url)
        if len(frasa) > 0 or jumlah_link >= MIN_LINK_LUAR_TERSEMBUNYI:
            temuan.append(
                {
                    "tag": tag.name,
                    "frasa": frasa,
                    "link_luar": jumlah_link,
                    "cuplikan": teks[:PANJANG_CUPLIKAN],
                }
            )
    return temuan


def cari_tag_tersembunyi_terluar(soup):
    """Kembalikan elemen tersembunyi yang induknya sendiri tidak tersembunyi."""
    hasil = []
    for tag in soup.find_all(True):
        if tag_tersembunyi(tag):
            if not punya_leluhur_tersembunyi(tag):
                hasil.append(tag)
    return hasil


def punya_leluhur_tersembunyi(tag):
    """True kalau salah satu induk elemen ini sudah tersembunyi."""
    for leluhur in tag.parents:
        if tag_tersembunyi(leluhur):
            return True
    return False


def tag_tersembunyi(tag):
    """True kalau atribut hidden atau style inline elemen ini menyembunyikannya dari pengunjung."""
    if tag.has_attr("hidden"):
        return True
    gaya = baca_gaya(tag.get("style"))
    if gaya.get("display") == "none":
        return True
    if gaya.get("visibility") == "hidden":
        return True
    if "font-size" in gaya and POLA_NOL.match(gaya["font-size"]):
        return True
    if "opacity" in gaya and POLA_NOL.match(gaya["opacity"]):
        return True
    for properti in PROPERTI_GESER:
        if properti in gaya:
            cocok = POLA_GESER_NEGATIF.match(gaya[properti])
            if cocok != None and float(cocok.group(1)) >= BATAS_GESER_KELUAR_LAYAR:
                return True
    return False


def baca_gaya(teks):
    """Ubah atribut style menjadi dict {properti: nilai}, berhuruf kecil dan tanpa spasi."""
    gaya = {}
    if teks == None:
        return gaya
    for deklarasi in teks.lower().split(";"):
        if ":" in deklarasi:
            properti, nilai = deklarasi.split(":", 1)
            nilai = nilai.replace("!important", "")
            gaya[properti.strip()] = "".join(nilai.split())
    return gaya


def hitung_link_luar(tag, url):
    """Hitung link absolut di dalam elemen yang menuju situs lain (link relatif dianggap situs sendiri)."""
    daftar_link = tag.find_all("a", href=True)
    if tag.name == "a" and tag.has_attr("href"):
        daftar_link.append(tag)
    jumlah = 0
    for link in daftar_link:
        href = link["href"].strip().lower()
        if href.startswith("http://") or href.startswith("https://") or href.startswith("//"):
            if not situs_sama(host_dari(url), host_dari(href)):
                jumlah = jumlah + 1
    return jumlah


def skrip_pengalih_referrer(html):
    """True kalau ada skrip yang memeriksa asal kunjungan, menyebut google, lalu memindahkan halaman."""
    # Hanya skrip inline yang bisa dibaca; skrip dari file luar tidak diunduh.
    if html == None or html == "":
        return False
    soup = BeautifulSoup(html, "html.parser")
    for skrip in soup.find_all("script"):
        kode = "".join(skrip.strings).lower()
        memeriksa_asal = False
        if "referrer" in kode or "referer" in kode:
            memeriksa_asal = True
        if memeriksa_asal and "google" in kode:
            if POLA_PINDAH_HALAMAN.search(kode) != None:
                return True
    return False


def nama_domain_berbau_judol(url):
    """True kalau nama domain URL mengandung kata berbau judol seperti slot atau gacor."""
    if url == None or url == "":
        return False
    # Hanya nama host yang diperiksa; kata "slot" di path situs sekolah bukan tanda.
    host = urlsplit(url).hostname
    if host == None:
        return False
    # Dilipat dengan normalisasi yang sama supaya samaran seperti s1otgac0r.com tetap kena.
    host_lipat = normalisasi(host)
    for kata in KATA_DOMAIN_JUDOL:
        if normalisasi(kata) in host_lipat:
            return True
    return False

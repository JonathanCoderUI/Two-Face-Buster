"""Situs tiruan di 127.0.0.1 yang sengaja berperilaku seperti situs siluman."""

# Pemilik: Pelapor. Rujukan: Panduan hlm. 12-16.
# Aturan situs uji: hanya jalan di 127.0.0.1, semua isi judol bertanda CONTOH UJI,
# semua link judol berakhiran .invalid.

import threading
import time
from urllib.parse import urlsplit

from flask import Flask, Response, request
from werkzeug.serving import make_server

app = Flask(__name__)

ALAMAT = "127.0.0.1"
PORT = 5050
DETIK_LAMBAT = 5

PENANDA_UJI = "CONTOH UJI"
# .invalid dijamin tidak pernah ada di internet (RFC 2606), jadi link ini tidak bisa nyasar ke situs asli.
ALAMAT_JUDOL = "http://slot-gacor-uji.invalid/daftar"

JUDUL_SEKOLAH = "Berita Sekolah"
SAMBUTAN = (
    "Selamat datang di situs resmi SMA Negeri Contoh. Kami berkomitmen menyediakan "
    "pendidikan yang bermutu, disiplin, dan berakhlak bagi seluruh siswa."
)
ISI_SEKOLAH = (
    "Upacara bendera rutin dilaksanakan setiap hari Senin pukul tujuh pagi di lapangan utama. "
    "Seluruh siswa dan guru wajib hadir mengenakan seragam lengkap. Kegiatan ekstrakurikuler "
    "pramuka, basket, dan paduan suara dimulai minggu depan di aula sekolah."
)
PENGUMUMAN = [
    "Pendaftaran peserta didik baru dibuka tanggal 1 Juni.",
    "Ujian akhir semester dimulai tanggal 8 Desember.",
    "Rapat orang tua siswa kelas sepuluh diadakan hari Sabtu.",
    "Perpustakaan tutup sementara selama masa renovasi.",
]

JUDUL_JUDOL = "SLOT GACOR MAXWIN - " + PENANDA_UJI
JUDUL_JUDOL_SAMARAN = "S1OT G4C0R M4XW1N - " + PENANDA_UJI
# Kalimat penutup bersama yang membuat versi judol jauh lebih panjang dan berbeda dari versi sekolah.
PENUTUP_JUDOL = (
    "Jackpot menanti Anda, mainkan sekarang juga, promo terbatas hanya hari ini, "
    "jangan sampai ketinggalan kesempatan emas bersama kami."
)
ISI_JUDOL = (
    PENANDA_UJI + ": Situs slot gacor hari ini, slot online dengan RTP live tertinggi, "
    "pola gacor anti rungkad, bonus new member 100 persen, deposit pulsa tanpa potongan, "
    "gampang menang scatter hitam. " + PENUTUP_JUDOL + " Daftar slot maxwin sekarang juga di "
    '<a href="' + ALAMAT_JUDOL + '">daftar slot gacor</a>.'
)

# Ejaan samaran: angka mirip huruf, huruf Kiril (о = o, а = a), dan karakter lebar nol (​).
ISI_JUDOL_SAMARAN = (
    PENANDA_UJI + ": S1OT G4C0R hari ini, S1OT 0NL1NE dengan R7P L1V3 tertinggi, "
    "P0L4 G4C0R 4NT1 RUNGK4D, B0NUS NEW M3MB3R 100 persen, D3P0S1T PULS4 tanpa potongan, "
    "s​lоt mаxwin dan slo​t gаcor. " + PENUTUP_JUDOL + " "
    'Daftar di <a href="' + ALAMAT_JUDOL + '">D4FT4R S1OT</a>.'
)

# Dua frasa promosi saja (slot online, bonus new member): artikel yang membahas bahaya judi.
JUDUL_EDUKASI = "Waspada Bahaya Judi Online"
ISI_EDUKASI = (
    "Guru BK mengingatkan siswa agar waspada terhadap iklan slot online dan janji bonus new member "
    "di media sosial. Judi merusak keuangan keluarga, mengganggu belajar, dan sulit dihentikan "
    "setelah kecanduan. Siswa yang menerima ajakan seperti ini diminta segera melapor kepada wali kelas."
)

# Tiga blok berpanjang sama yang bergilir tiap permintaan, sehingga dua kunjungan berurutan berbeda sedikit.
BLOK_DINAMIS = [
    "Jam sekolah hari ini pukul tujuh sampai tiga sore, kantin buka seperti biasa.",
    "Jadwal piket kelas berubah minggu ini, silakan cek papan pengumuman sekolah.",
    "Cuaca hari ini mendung, siswa dianjurkan membawa jas hujan dan payung.",
]
hitungan_dinamis = {"jumlah": 0}
kunci_hitungan = threading.Lock()


def halaman(judul, isi, n, tambahan=""):
    """Kembalikan HTML halaman sekolah dengan judul, isi, dan pengumuman ke-n."""
    pengumuman = PENGUMUMAN[(n - 1) % len(PENGUMUMAN)]
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        "<title>" + judul + "</title></head><body>"
        "<h1>SMA Negeri Contoh</h1><p>" + SAMBUTAN + "</p>"
        "<h2>" + judul + "</h2><p>" + isi + "</p>"
        "<h3>Pengumuman</h3><ul><li>" + pengumuman + "</li></ul>"
        + tambahan +
        "</body></html>"
    )


def dari_googlebot():
    """True kalau User-Agent permintaan memuat googlebot."""
    agen = request.headers.get("User-Agent", "")
    if "googlebot" in agen.lower():
        return True
    return False


def dari_google():
    """True kalau Referer permintaan berasal dari Google."""
    asal = request.headers.get("Referer", "")
    host = urlsplit(asal).hostname
    if host == None:
        return False
    if "google" in host.split("."):
        return True
    return False


@app.route("/")
def beranda():
    """Daftar semua jalur situs uji, untuk dicoba manual di browser."""
    jalur = [
        "normal", "dinamis", "edukasi", "cloak-ua", "cloak-samaran",
        "cloak-referer", "tersembunyi", "terbuka", "rahasia", "lambat",
    ]
    tautan = ""
    for nama in jalur:
        tautan = tautan + '<li><a href="/' + nama + '/1">/' + nama + "/1</a></li>"
    return halaman("Situs Uji", "Halaman uji Situs Siluman. " + PENANDA_UJI + ".", 1, "<ul>" + tautan + "</ul>")


@app.route("/normal/<int:n>")
def normal(n):
    """Halaman sekolah biasa, sama untuk semua pengunjung."""
    return halaman(JUDUL_SEKOLAH, ISI_SEKOLAH, n)


@app.route("/dinamis/<int:n>")
def dinamis(n):
    """Halaman jujur yang sedikit berubah tiap dikunjungi (kemiripan sekitar 85%)."""
    with kunci_hitungan:
        urutan = hitungan_dinamis["jumlah"]
        hitungan_dinamis["jumlah"] = urutan + 1
    blok = BLOK_DINAMIS[urutan % len(BLOK_DINAMIS)]
    return halaman(JUDUL_SEKOLAH, ISI_SEKOLAH + " " + blok, n)


@app.route("/edukasi/<int:n>")
def edukasi(n):
    """Artikel tentang bahaya judi yang menyebut dua frasa promosi; harus tetap aman."""
    return halaman(JUDUL_EDUKASI, ISI_EDUKASI, n)


@app.route("/cloak-ua/<int:n>")
def cloak_ua(n):
    """Isi judol hanya untuk User-Agent Googlebot; yang lain melihat halaman sekolah."""
    if dari_googlebot():
        return halaman(JUDUL_JUDOL, ISI_JUDOL, n)
    return halaman(JUDUL_SEKOLAH, ISI_SEKOLAH, n)


@app.route("/cloak-samaran/<int:n>")
def cloak_samaran(n):
    """Seperti cloak-ua, tapi judolnya ditulis dengan ejaan samaran."""
    if dari_googlebot():
        return halaman(JUDUL_JUDOL_SAMARAN, ISI_JUDOL_SAMARAN, n)
    return halaman(JUDUL_SEKOLAH, ISI_SEKOLAH, n)


@app.route("/cloak-referer/<int:n>")
def cloak_referer(n):
    """Pengunjung dari Google dialihkan ke situs judol; browser biasa dan Googlebot tidak."""
    if dari_google() and not dari_googlebot():
        # Badan kosong: crawler hanya perlu mencatat Location, tidak mengunjunginya.
        return Response("", status=302, headers={"Location": ALAMAT_JUDOL})
    return halaman(JUDUL_SEKOLAH, ISI_SEKOLAH, n)


@app.route("/tersembunyi/<int:n>")
def tersembunyi(n):
    """Teks dan link judol di elemen display:none, sama untuk semua pengunjung."""
    blok = (
        '<div style="display:none">' + PENANDA_UJI + ": slot gacor, slot online, "
        "bonus new member, deposit pulsa. "
        '<a href="' + ALAMAT_JUDOL + '">daftar sekarang</a></div>'
    )
    return halaman(JUDUL_SEKOLAH, ISI_SEKOLAH, n, blok)


@app.route("/terbuka/<int:n>")
def terbuka(n):
    """Isi judol terlihat oleh semua pengunjung, tanpa cloaking."""
    return halaman(JUDUL_JUDOL, ISI_JUDOL, n)


@app.route("/rahasia/<int:n>")
def rahasia(n):
    """Halaman biasa yang dilarang di robots.txt; crawler tidak boleh mengunjunginya."""
    return halaman("Halaman Internal", ISI_SEKOLAH, n)


@app.route("/lambat/<int:n>")
def lambat(n):
    """Halaman yang menjawab sangat lambat, untuk menguji batas waktu crawler."""
    time.sleep(DETIK_LAMBAT)
    return halaman(JUDUL_SEKOLAH, ISI_SEKOLAH, n)


@app.route("/robots.txt")
def robots():
    """robots.txt yang melarang /rahasia/."""
    return Response("User-agent: *\nDisallow: /rahasia/\n", mimetype="text/plain")


def jalankan_di_latar():
    """Jalankan situs uji di thread terpisah pada port acak, lalu kembalikan (server, alamat)."""
    # Port 0 = biarkan sistem operasi memilih port kosong, supaya tes tidak bentrok dengan port 5050.
    server = make_server(ALAMAT, 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    alamat = "http://" + ALAMAT + ":" + str(server.server_port)
    return server, alamat


if __name__ == "__main__":
    # Hanya 127.0.0.1: situs ini sengaja menyajikan konten judol contoh.
    app.run(host=ALAMAT, port=PORT, threaded=True)

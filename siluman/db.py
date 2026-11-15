"""Satu-satunya pintu ke database SQLite: skema tiga tabel dan semua fungsi baca/tulis."""

# File BERSAMA. Perubahan wajib lewat PR yang disetujui dua anggota lain.
# Rujukan: Panduan hlm. 4-7.

# TODO 1:
# Tulis skema tiga tabel (kunjungan, hasil, laporan) dan indeks (putaran, url)
# persis seperti Panduan hlm. 5.
SKEMA = ...


def buka(lokasi):
    """Buka koneksi SQLite di lokasi, buat tabel kalau belum ada, lalu kembalikan koneksinya."""
    # TODO 2:
    # Buat folder induknya kalau belum ada, aktifkan mode WAL, jalankan SKEMA,
    # dan pastikan baris hasil query bisa dibaca dengan nama kolom (baris["url"]).
    ...


def simpan_kunjungan(conn, k):
    """Simpan satu dict kunjungan ke tabel kunjungan."""
    # TODO 3:
    # HTML disimpan terkompres zlib. HTML boleh None kalau kunjungannya gagal.
    ...


def ambil_versi(conn, putaran, url):
    """Kembalikan {"browser": k, "googlebot": k, "dari_google": k} untuk satu URL."""
    # TODO 4:
    # HTML sudah dibuka dari zlib. Persona yang tidak ditemukan bernilai None.
    ...


def simpan_hasil(conn, h):
    """Simpan atau perbarui satu baris di tabel hasil."""
    # TODO 5:
    # Kolom alasan disimpan sebagai JSON. Kolom verifikasi TIDAK boleh tertimpa.
    ...


def tandai_verifikasi(conn, putaran, url, nilai):
    """Isi kolom verifikasi satu URL dengan "benar" atau "salah"."""
    # TODO 6:
    # Dipakai tombol verifikasi di dashboard.
    ...


def catat_laporan(conn, domain, status, catatan, tanggal):
    """Simpan atau perbarui status surat untuk satu domain."""
    # TODO 7:
    # Status: draf, terkirim, dibalas, bersih, eskalasi.
    ...


def url_dicurigai(conn, putaran):
    """Kembalikan daftar URL berlabel hampir_pasti atau perlu_dicek di satu putaran."""
    # TODO 8:
    # Dipakai perintah bukti di main.py.
    ...


def nama_folder(url):
    """Ubah URL menjadi nama folder yang aman dipakai di folder bukti/."""
    # TODO 9
    ...

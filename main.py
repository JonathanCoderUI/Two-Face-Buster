"""Pintu masuk perintah terminal Situs Siluman."""

# File BERSAMA. Hanya memanggil fungsi modul lain, tidak berisi logika deteksi.
# Rujukan: Panduan hlm. 35-37.


def baca_url(lokasi):
    """Baca kolom url dari file CSV lalu kembalikan daftar URL-nya."""
    # TODO 1:
    # Lewati baris yang kosong.
    ...


def main():
    """Baca argumen terminal lalu jalankan satu tahap."""
    # TODO 2:
    # Opsi umum --db dan --putaran yang dipakai semua subperintah.
    ...

    # TODO 3:
    # Subperintah: scan (--input, --jeda), nilai (--model), bukti, laporan,
    # ekspor-label (--keluar), latih (--data, --keluar).
    ...

    # TODO 4:
    # Buka database lewat db.buka, lalu panggil fungsi modul yang sesuai.
    # Import modul di dalam cabang subperintahnya, supaya perintah lain tetap jalan
    # walau library-nya belum terpasang.
    ...

    # TODO 5:
    # Tutup koneksi database.
    ...


if __name__ == "__main__":
    main()

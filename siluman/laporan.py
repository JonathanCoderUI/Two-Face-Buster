"""Menyusun surat untuk admin situs dari temuan yang sudah diverifikasi benar."""

# Pemilik: Pelapor. Rujukan: Panduan hlm. 33-35.

# TODO 1:
# Nama dan email resmi tim. Wajib diisi sebelum surat pertama dikirim.
TIM = ...


def buat_semua(conn, putaran):
    """Buat satu surat per domain lalu kembalikan jumlah surat yang dibuat."""
    # TODO 2 (Minggu 3):
    # Hanya temuan hampir_pasti atau perlu_dicek yang verifikasinya "benar".
    # Render templates/laporan.md.j2 ke laporan_keluar/<domain>.md, lalu catat status draf.
    ...

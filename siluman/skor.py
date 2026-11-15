"""Menjumlahkan poin tiap kejanggalan menjadi skor, label, dan alasan."""

# Pemilik: Detektif.

# TODO 1:
# Kumpulkan di sini semua angka yang bisa disetel: ambang "isinya judol" 0,5,
# ambang "dua versi sangat berbeda" 0,5, batas label (60 hampir_pasti,
# 25 perlu_dicek), dan poin kesembilan tanda dari tabel poin.
...


def nilai_url(versi, model=None):
    """Kembalikan dict skor, label, alasan, kemiripan, p_judol_browser, p_judol_googlebot untuk satu URL."""
    # TODO 2 (Minggu 1, versi kata kunci):
    # versi adalah hasil db.ambil_versi. alasan berbentuk [{"poin": 50, "teks": "..."}].
    # Kalau versi browser atau Googlebot gagal diambil: label tidak_bisa_dicek, tidak pernah aman.
    ...

    # TODO 3 (Minggu 2):
    # Lengkapi kesembilan tanda dari tabel poin.
    ...


def nilai_semua(conn, putaran, model=None):
    """Nilai semua URL di satu putaran, simpan ke tabel hasil, lalu kembalikan jumlah URL per label."""
    # TODO 4:
    # Simpan tiap hasil lewat db.simpan_hasil.
    ...

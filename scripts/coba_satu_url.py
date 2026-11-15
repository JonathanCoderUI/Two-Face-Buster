"""Coba satu URL situs uji dengan tiga persona lalu cetak hasilnya."""

# Pemilik: Penjelajah.
# Jalankan dengan: python -m scripts.coba_satu_url (situs uji harus sedang hidup).


async def coba():
    """Kunjungi satu URL situs uji sebagai tiga persona lalu cetak hasilnya."""
    # TODO 1:
    # Untuk persona browser, googlebot, dan dari_google: panggil crawler.ambil pada
    # http://127.0.0.1:5050/cloak-referer/1, lalu cetak persona, status, redirect_ke,
    # dan apakah HTML-nya kosong.
    ...

# TODO 2:
# Jalankan coba() dengan asyncio.

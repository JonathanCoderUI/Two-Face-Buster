"""Tangkapan layar versi browser dan versi Googlebot untuk URL yang dicurigai."""

# Pemilik: Pelapor (Minggu 2). Rujukan: Panduan hlm. 30-31.


async def tangkap(browser, url, persona, lokasi_file):
    """Simpan tangkapan layar satu URL sebagai satu persona."""
    # TODO 1:
    # Blokir semua permintaan ke situs lain, termasuk situs judi, sebelum terkirim.
    ...


async def kumpulkan_bukti(daftar_url, folder="bukti"):
    """Simpan browser.png dan googlebot.png untuk setiap URL di folder bukti/."""
    # TODO 2:
    # Playwright headless yang bersih tanpa akun login. Satu folder per URL lewat db.nama_folder.
    ...

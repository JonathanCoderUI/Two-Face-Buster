"""Pembantu tes: mengunjungi situs uji sebagai tiga persona tanpa mengikuti redirect."""

import http.client
from urllib.parse import urlsplit

from siluman.config import PERSONA, URUTAN_PERSONA


def ambil_mentah(alamat, jalur, persona, timeout=10):
    """Kunjungi satu jalur sebagai satu persona; kembalikan (status, header Location, isi teks)."""
    bagian = urlsplit(alamat)
    sambungan = http.client.HTTPConnection(bagian.hostname, bagian.port, timeout=timeout)
    try:
        # http.client tidak mengikuti redirect, jadi 302 terlihat apa adanya.
        sambungan.request("GET", jalur, headers=PERSONA[persona])
        jawaban = sambungan.getresponse()
        isi = jawaban.read().decode("utf-8")
        return jawaban.status, jawaban.getheader("Location"), isi
    finally:
        sambungan.close()


def ambil_versi(alamat, jalur):
    """Kembalikan {"browser": k, "googlebot": k, "dari_google": k} berbentuk dict tabel kunjungan."""
    versi = {}
    # Urutan sama dengan crawler, penting untuk halaman /dinamis/ yang berubah tiap permintaan.
    for persona in URUTAN_PERSONA:
        status, lokasi, isi = ambil_mentah(alamat, jalur, persona)
        kunjungan = {
            "putaran": 1,
            "url": alamat + jalur,
            "domain": urlsplit(alamat).hostname,
            "persona": persona,
            "waktu": "2026-11-27T10:00:00",
            "status": status,
            "url_akhir": alamat + jalur,
            "redirect_ke": None,
            "html": isi,
            "catatan": None,
        }
        if lokasi != None:
            # Redirect ke situs lain dicatat, tidak diikuti, dan tidak punya HTML (seperti crawler).
            kunjungan["redirect_ke"] = lokasi
            kunjungan["html"] = None
        versi[persona] = kunjungan
    return versi

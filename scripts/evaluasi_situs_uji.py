"""Hitung precision dan recall detektor di halaman situs uji."""

# Pemilik: Detektif (Minggu 2).
# Jalankan dengan: python -m scripts.evaluasi_situs_uji (situs uji harus sedang hidup).

import asyncio
import os
import tempfile

from siluman import config, crawler, db, skor

ALAMAT_UJI = "http://127.0.0.1:5050"
PUTARAN = 1

# Jenis halaman dan jumlahnya: 30 halaman bertrik dan 30 halaman jujur.
HALAMAN_BERTRIK = {
    "cloak-ua": 6,
    "cloak-samaran": 6,
    "cloak-referer": 6,
    "tersembunyi": 6,
    "terbuka": 6,
}
HALAMAN_JUJUR = {
    "normal": 10,
    "dinamis": 10,
    "edukasi": 10,
}

# "Ditandai" berarti label hampir_pasti atau perlu_dicek.
LABEL_DITANDAI = [skor.LABEL_HAMPIR_PASTI, skor.LABEL_PERLU_DICEK]


def buat_daftar_alamat(jumlah_per_jenis):
    """Kembalikan daftar URL situs uji, misalnya http://127.0.0.1:5050/cloak-ua/1."""
    daftar = []
    for jenis in jumlah_per_jenis:
        for nomor in range(1, jumlah_per_jenis[jenis] + 1):
            daftar.append(ALAMAT_UJI + "/" + jenis + "/" + str(nomor))
    return daftar


def label_ditandai(label):
    """True kalau label berarti halaman ditandai mencurigakan."""
    if label in LABEL_DITANDAI:
        return True
    return False


def hitung_matriks(pasangan):
    """Hitung TP, FP, FN, TN dari daftar pasangan (bertrik, ditandai)."""
    matriks = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for bertrik, ditandai in pasangan:
        if bertrik and ditandai:
            matriks["tp"] = matriks["tp"] + 1
        elif not bertrik and ditandai:
            matriks["fp"] = matriks["fp"] + 1
        elif bertrik and not ditandai:
            matriks["fn"] = matriks["fn"] + 1
        else:
            matriks["tn"] = matriks["tn"] + 1
    return matriks


def hitung_precision(matriks):
    """Kembalikan TP / (TP + FP), atau None kalau tidak ada halaman yang ditandai."""
    pembagi = matriks["tp"] + matriks["fp"]
    if pembagi == 0:
        return None
    return matriks["tp"] / pembagi


def hitung_recall(matriks):
    """Kembalikan TP / (TP + FN), atau None kalau tidak ada halaman bertrik."""
    pembagi = matriks["tp"] + matriks["fn"]
    if pembagi == 0:
        return None
    return matriks["tp"] / pembagi


def format_persen(nilai):
    """Ubah 0 sampai 1 menjadi teks persen, atau 'tidak terdefinisi' untuk None."""
    if nilai == None:
        return "tidak terdefinisi"
    return str(round(nilai * 100, 1)) + "%"


def kumpulkan_pasangan(conn, alamat_bertrik, alamat_jujur):
    """Baca label dari tabel hasil; kembalikan (daftar pasangan, daftar URL tanpa hasil)."""
    pasangan = []
    tanpa_hasil = []
    kelompok = [(True, alamat_bertrik), (False, alamat_jujur)]
    for bertrik, daftar in kelompok:
        for url in daftar:
            baris = conn.execute(
                "SELECT label FROM hasil WHERE putaran = ? AND url = ?",
                (PUTARAN, url),
            ).fetchone()
            if baris == None:
                tanpa_hasil.append(url)
            else:
                pasangan.append((bertrik, label_ditandai(baris["label"])))
    return pasangan, tanpa_hasil


def main():
    """Scan halaman situs uji, nilai, lalu cetak precision dan recall."""
    alamat_bertrik = buat_daftar_alamat(HALAMAN_BERTRIK)
    alamat_jujur = buat_daftar_alamat(HALAMAN_JUJUR)

    # Database sementara: tidak mengotori data/siluman.db.
    with tempfile.TemporaryDirectory() as folder:
        conn = db.buka(os.path.join(folder, "evaluasi.db"))
        asyncio.run(crawler.scan(alamat_bertrik + alamat_jujur, conn, PUTARAN, config.JEDA_PER_DOMAIN))
        skor.nilai_semua(conn, PUTARAN)
        pasangan, tanpa_hasil = kumpulkan_pasangan(conn, alamat_bertrik, alamat_jujur)
        conn.close()

    matriks = hitung_matriks(pasangan)
    print("TP =", matriks["tp"], " FP =", matriks["fp"], " FN =", matriks["fn"], " TN =", matriks["tn"])
    print("Precision:", format_persen(hitung_precision(matriks)))
    print("Recall   :", format_persen(hitung_recall(matriks)))
    if len(tanpa_hasil) > 0:
        print("Peringatan:", len(tanpa_hasil), "URL tidak punya hasil dan tidak dihitung.")


if __name__ == "__main__":
    main()

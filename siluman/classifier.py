"""Model ML opsional (Minggu 4) sebagai pembanding metode kata kunci."""

# Pemilik: Detektif.
# sklearn dan joblib diimpor di dalam fungsi, supaya skor.py tetap bisa dipakai tanpa keduanya.

import csv
import os
import random

from siluman import db
from siluman.fitur import ekstrak_teks_terlihat
from siluman.normalisasi import nilai_judol_kata_kunci, normalisasi

# ---- Angka yang bisa disetel ----
JUMLAH_AMAN_ACAK = 200      # URL tidak dicurigai yang ikut diekspor untuk dilabeli
BENIH_ACAK = 0              # tetap, supaya ekspor yang diulang memilih URL aman yang sama
PERSONA_DILABELI = ["browser", "googlebot"]
PANJANG_MAKS_TEKS = 5000    # karakter per baris CSV, supaya mudah dibuka di spreadsheet
NGRAM_MIN = 3
NGRAM_MAKS = 5
JUMLAH_LIPATAN_MAKS = 5
AMBANG_PELUANG = 0.5        # peluang judol minimal agar model menjawab "judol"

LABEL_JUDOL = "judol"
LABEL_AMAN = "aman"
KOLOM_CSV = ["domain", "url", "persona", "label", "teks"]


def ekspor_untuk_label(conn, putaran, lokasi_keluar):
    """Tulis CSV berisi teks yang akan dilabeli manusia dan kembalikan jumlah barisnya."""
    dicurigai = db.url_dicurigai(conn, putaran)
    sudah_dicurigai = set(dicurigai)
    kandidat_aman = []
    for url in db.daftar_url(conn, putaran):
        if url not in sudah_dicurigai:
            kandidat_aman.append(url)
    jumlah_aman = min(JUMLAH_AMAN_ACAK, len(kandidat_aman))
    aman_terpilih = random.Random(BENIH_ACAK).sample(kandidat_aman, jumlah_aman)

    folder = os.path.dirname(lokasi_keluar)
    if folder != "":
        os.makedirs(folder, exist_ok=True)

    jumlah_baris = 0
    # utf-8-sig: spreadsheet membaca huruf non-ASCII dengan benar, dan csv.DictReader tetap bisa membacanya.
    with open(lokasi_keluar, "w", newline="", encoding="utf-8-sig") as berkas:
        penulis = csv.DictWriter(berkas, fieldnames=KOLOM_CSV)
        penulis.writeheader()
        for url in dicurigai + aman_terpilih:
            jumlah_baris = jumlah_baris + tulis_baris_url(penulis, conn, putaran, url)
    return jumlah_baris


def tulis_baris_url(penulis, conn, putaran, url):
    """Tulis satu baris per persona yang punya teks terlihat, lalu kembalikan jumlah barisnya."""
    versi = db.ambil_versi(conn, putaran, url)
    jumlah = 0
    for persona in PERSONA_DILABELI:
        kunjungan = versi[persona]
        if kunjungan == None or kunjungan["html"] == None:
            continue
        teks = ekstrak_teks_terlihat(kunjungan["html"])
        if teks == "":
            continue
        domain = kunjungan["domain"]
        if domain == None:
            domain = ""
        penulis.writerow({
            "domain": domain,
            "url": url,
            "persona": persona,
            "label": "",
            "teks": teks[:PANJANG_MAKS_TEKS],
        })
        jumlah = jumlah + 1
    return jumlah


def baca_data_berlabel(lokasi_csv):
    """Baca CSV yang sudah dilabeli lalu kembalikan (daftar teks, daftar 0/1, daftar domain)."""
    daftar_teks = []
    daftar_kelas = []
    daftar_domain = []
    with open(lokasi_csv, newline="", encoding="utf-8-sig") as berkas:
        pembaca = csv.DictReader(berkas)
        nomor_baris = 1  # baris 1 adalah judul kolom
        for baris in pembaca:
            nomor_baris = nomor_baris + 1
            label = baris.get("label")
            if label == None:
                label = ""
            label = label.strip().lower()
            if label == "":
                continue  # belum dilabeli
            if label == LABEL_JUDOL:
                kelas = 1
            elif label == LABEL_AMAN:
                kelas = 0
            else:
                raise ValueError(
                    "Baris " + str(nomor_baris) + ": label harus 'judol' atau 'aman', bukan " + repr(label)
                )
            daftar_teks.append(baris["teks"])
            daftar_kelas.append(kelas)
            daftar_domain.append(baris["domain"])
    return daftar_teks, daftar_kelas, daftar_domain


def buat_model():
    """Buat model baru: TF-IDF huruf per kata (n-gram 3-5) lalu regresi logistik."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    # normalisasi sebagai preprocessor: ejaan samaran dilipat dulu, dengan aturan yang sama dengan kata kunci.
    # class_weight="balanced": halaman judol jauh lebih jarang daripada halaman aman.
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(NGRAM_MIN, NGRAM_MAKS), preprocessor=normalisasi)),
        ("regresi", LogisticRegression(class_weight="balanced", max_iter=1000)),
    ])


def bagi_per_domain(daftar_domain, jumlah_lipatan):
    """Bagi indeks data menjadi lipatan (latih, uji) dengan satu domain hanya di satu lipatan uji."""
    from sklearn.model_selection import GroupKFold

    indeks = list(range(len(daftar_domain)))
    lipatan = []
    for indeks_latih, indeks_uji in GroupKFold(n_splits=jumlah_lipatan).split(indeks, groups=daftar_domain):
        lipatan.append((indeks_latih.tolist(), indeks_uji.tolist()))
    return lipatan


def peluang_banyak(model, daftar_teks):
    """Kembalikan peluang judol (0 sampai 1) untuk tiap teks di daftar_teks."""
    semua = model.predict_proba(daftar_teks)
    posisi_judol = 1
    for posisi in range(len(model.classes_)):
        if model.classes_[posisi] == 1:
            posisi_judol = posisi
    hasil = []
    for baris in semua:
        hasil.append(float(baris[posisi_judol]))
    return hasil


def peluang_judol(model, teks):
    """Kembalikan peluang (0 sampai 1) bahwa satu teks adalah isi judol."""
    return peluang_banyak(model, [teks])[0]


def hitung_precision_recall(kelas_benar, kelas_tebakan):
    """Hitung precision dan recall untuk kelas judol (None kalau pembaginya nol)."""
    benar_positif = 0
    salah_positif = 0
    salah_negatif = 0
    for i in range(len(kelas_benar)):
        if kelas_tebakan[i] == 1 and kelas_benar[i] == 1:
            benar_positif = benar_positif + 1
        elif kelas_tebakan[i] == 1 and kelas_benar[i] == 0:
            salah_positif = salah_positif + 1
        elif kelas_tebakan[i] == 0 and kelas_benar[i] == 1:
            salah_negatif = salah_negatif + 1
    precision = None
    if benar_positif + salah_positif > 0:
        precision = benar_positif / (benar_positif + salah_positif)
    recall = None
    if benar_positif + salah_negatif > 0:
        recall = benar_positif / (benar_positif + salah_negatif)
    return {"precision": precision, "recall": recall}


def format_persen(nilai):
    """Ubah angka 0 sampai 1 menjadi teks persen, atau '-' kalau tidak ada."""
    if nilai == None:
        return "-"
    return str(round(nilai * 100, 1)) + "%"


def latih_dan_evaluasi(lokasi_csv, lokasi_model):
    """Latih model, cetak precision dan recall dibanding metode kata kunci, lalu simpan modelnya."""
    import joblib

    # Diimpor di sini karena skor.py mengimpor modul ini.
    from siluman.skor import AMBANG_JUDOL

    daftar_teks, kelas_benar, daftar_domain = baca_data_berlabel(lokasi_csv)
    if len(set(kelas_benar)) < 2:
        raise ValueError("Butuh minimal satu contoh berlabel 'judol' dan satu 'aman'")
    jumlah_domain = len(set(daftar_domain))
    if jumlah_domain < 2:
        raise ValueError("Butuh data dari minimal dua domain untuk evaluasi per domain")

    jumlah_lipatan = min(JUMLAH_LIPATAN_MAKS, jumlah_domain)
    tebakan_model = [0] * len(daftar_teks)
    for indeks_latih, indeks_uji in bagi_per_domain(daftar_domain, jumlah_lipatan):
        teks_latih = []
        kelas_latih = []
        for i in indeks_latih:
            teks_latih.append(daftar_teks[i])
            kelas_latih.append(kelas_benar[i])
        if len(set(kelas_latih)) < 2:
            raise ValueError("Satu lipatan latih hanya berisi satu kelas; tambah data berlabel")
        model_lipatan = buat_model()
        model_lipatan.fit(teks_latih, kelas_latih)
        teks_uji = []
        for i in indeks_uji:
            teks_uji.append(daftar_teks[i])
        peluang = peluang_banyak(model_lipatan, teks_uji)
        for urutan in range(len(indeks_uji)):
            if peluang[urutan] >= AMBANG_PELUANG:
                tebakan_model[indeks_uji[urutan]] = 1

    tebakan_kata_kunci = []
    for teks in daftar_teks:
        if nilai_judol_kata_kunci(teks) >= AMBANG_JUDOL:
            tebakan_kata_kunci.append(1)
        else:
            tebakan_kata_kunci.append(0)

    hasil = {
        "jumlah": len(daftar_teks),
        "model": hitung_precision_recall(kelas_benar, tebakan_model),
        "kata_kunci": hitung_precision_recall(kelas_benar, tebakan_kata_kunci),
    }
    print("Data berlabel:", hasil["jumlah"], "baris dari", jumlah_domain, "domain;", jumlah_lipatan, "lipatan per domain")
    for nama in ["kata_kunci", "model"]:
        print(
            nama.ljust(11),
            "precision", format_persen(hasil[nama]["precision"]),
            "recall", format_persen(hasil[nama]["recall"]),
        )

    model_akhir = buat_model()
    model_akhir.fit(daftar_teks, kelas_benar)
    folder = os.path.dirname(lokasi_model)
    if folder != "":
        os.makedirs(folder, exist_ok=True)
    joblib.dump(model_akhir, lokasi_model)
    return hasil


def muat_model(lokasi):
    """Muat model yang sudah disimpan oleh latih_dan_evaluasi."""
    import joblib

    # joblib memakai pickle: hanya muat model buatan sendiri, jangan file dari sumber lain.
    return joblib.load(lokasi)

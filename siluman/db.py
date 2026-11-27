"""Satu-satunya pintu ke database SQLite: skema tiga tabel dan semua fungsi baca/tulis."""

# File BERSAMA. Perubahan wajib lewat PR yang disetujui dua anggota lain.
# Rujukan: Panduan hlm. 4-7.

import json
import os
import re
import sqlite3
import zlib
from urllib.parse import urlsplit

PERSONA_SEMUA = ["browser", "googlebot", "dari_google"]
LABEL_DICURIGAI = ["hampir_pasti", "perlu_dicek"]
STATUS_VERIFIKASI = ["benar", "salah"]
STATUS_LAPORAN = ["draf", "terkirim", "dibalas", "bersih", "eskalasi"]
PANJANG_MAKS_NAMA_FOLDER = 100

SKEMA = """
CREATE TABLE IF NOT EXISTS kunjungan (
    putaran     INTEGER NOT NULL,
    url         TEXT    NOT NULL,
    domain      TEXT,
    persona     TEXT    NOT NULL,
    waktu       TEXT,
    status      INTEGER,
    url_akhir   TEXT,
    redirect_ke TEXT,
    html        BLOB,
    catatan     TEXT,
    PRIMARY KEY (putaran, url, persona)
);

CREATE TABLE IF NOT EXISTS hasil (
    putaran            INTEGER NOT NULL,
    url                TEXT    NOT NULL,
    domain             TEXT,
    skor               INTEGER,
    label              TEXT,
    alasan             TEXT,
    kemiripan          REAL,
    p_judol_browser    REAL,
    p_judol_googlebot  REAL,
    waktu              TEXT,
    verifikasi         TEXT,
    PRIMARY KEY (putaran, url)
);

CREATE TABLE IF NOT EXISTS laporan (
    domain   TEXT PRIMARY KEY,
    status   TEXT,
    catatan  TEXT,
    tanggal  TEXT
);

CREATE INDEX IF NOT EXISTS idx_kunjungan_putaran_url ON kunjungan (putaran, url);
CREATE INDEX IF NOT EXISTS idx_hasil_putaran_label ON hasil (putaran, label);
"""


def buka(lokasi):
    """Buka koneksi SQLite di lokasi, buat tabel kalau belum ada, lalu kembalikan koneksinya."""
    # ":memory:" tidak punya folder induk, jadi dilewati.
    if lokasi != ":memory:":
        folder = os.path.dirname(lokasi)
        if folder != "":
            os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(lokasi)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SKEMA)
    conn.commit()
    return conn


def simpan_kunjungan(conn, k):
    """Simpan satu dict kunjungan ke tabel kunjungan."""
    html_terkompres = None
    if k.get("html") != None:
        html_terkompres = zlib.compress(k["html"].encode("utf-8"))
    # REPLACE: kunjungan ulang untuk (putaran, url, persona) yang sama menggantikan yang lama.
    conn.execute(
        "INSERT OR REPLACE INTO kunjungan "
        "(putaran, url, domain, persona, waktu, status, url_akhir, redirect_ke, html, catatan) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            k["putaran"],
            k["url"],
            k.get("domain"),
            k["persona"],
            k.get("waktu"),
            k.get("status"),
            k.get("url_akhir"),
            k.get("redirect_ke"),
            html_terkompres,
            k.get("catatan"),
        ),
    )
    conn.commit()


def ambil_versi(conn, putaran, url):
    """Kembalikan {"browser": k, "googlebot": k, "dari_google": k} untuk satu URL."""
    versi = {}
    for persona in PERSONA_SEMUA:
        versi[persona] = None

    baris_semua = conn.execute(
        "SELECT * FROM kunjungan WHERE putaran = ? AND url = ?",
        (putaran, url),
    ).fetchall()
    for baris in baris_semua:
        k = dict(baris)
        if k["html"] != None:
            k["html"] = zlib.decompress(k["html"]).decode("utf-8")
        versi[k["persona"]] = k
    return versi


def simpan_hasil(conn, h):
    """Simpan atau perbarui satu baris di tabel hasil."""
    # Kolom verifikasi sengaja tidak ada di INSERT maupun DO UPDATE: isinya dari manusia.
    conn.execute(
        "INSERT INTO hasil "
        "(putaran, url, domain, skor, label, alasan, kemiripan, p_judol_browser, p_judol_googlebot, waktu) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT (putaran, url) DO UPDATE SET "
        "domain = excluded.domain, skor = excluded.skor, label = excluded.label, "
        "alasan = excluded.alasan, kemiripan = excluded.kemiripan, "
        "p_judol_browser = excluded.p_judol_browser, "
        "p_judol_googlebot = excluded.p_judol_googlebot, waktu = excluded.waktu",
        (
            h["putaran"],
            h["url"],
            h.get("domain"),
            h.get("skor"),
            h.get("label"),
            json.dumps(h.get("alasan", []), ensure_ascii=False),
            h.get("kemiripan"),
            h.get("p_judol_browser"),
            h.get("p_judol_googlebot"),
            h.get("waktu"),
        ),
    )
    conn.commit()


def tandai_verifikasi(conn, putaran, url, nilai):
    """Isi kolom verifikasi satu URL dengan "benar" atau "salah"."""
    if nilai not in STATUS_VERIFIKASI:
        raise ValueError("verifikasi harus 'benar' atau 'salah', bukan " + repr(nilai))
    conn.execute(
        "UPDATE hasil SET verifikasi = ? WHERE putaran = ? AND url = ?",
        (nilai, putaran, url),
    )
    conn.commit()


def catat_laporan(conn, domain, status, catatan, tanggal):
    """Simpan atau perbarui status surat untuk satu domain."""
    if status not in STATUS_LAPORAN:
        raise ValueError("status laporan tidak dikenal: " + repr(status))
    conn.execute(
        "INSERT INTO laporan (domain, status, catatan, tanggal) VALUES (?, ?, ?, ?) "
        "ON CONFLICT (domain) DO UPDATE SET "
        "status = excluded.status, catatan = excluded.catatan, tanggal = excluded.tanggal",
        (domain, status, catatan, tanggal),
    )
    conn.commit()


def url_dicurigai(conn, putaran):
    """Kembalikan daftar URL berlabel hampir_pasti atau perlu_dicek di satu putaran."""
    baris_semua = conn.execute(
        "SELECT url FROM hasil WHERE putaran = ? AND label IN (?, ?) ORDER BY skor DESC, url",
        (putaran, LABEL_DICURIGAI[0], LABEL_DICURIGAI[1]),
    ).fetchall()
    daftar = []
    for baris in baris_semua:
        daftar.append(baris["url"])
    return daftar


def daftar_url(conn, putaran):
    """Kembalikan daftar URL yang dikunjungi di satu putaran, tanpa duplikat."""
    # Fungsi BARU di luar kontrak awal; dibutuhkan skor.nilai_semua.
    baris_semua = conn.execute(
        "SELECT DISTINCT url FROM kunjungan WHERE putaran = ? ORDER BY url",
        (putaran,),
    ).fetchall()
    daftar = []
    for baris in baris_semua:
        daftar.append(baris["url"])
    return daftar


def nama_folder(url):
    """Ubah URL menjadi nama folder yang aman dipakai di folder bukti/."""
    bagian = urlsplit(url)
    mentah = (bagian.hostname or "") + bagian.path
    # Hanya huruf, angka, titik, dan strip yang lolos; sisanya jadi satu garis bawah.
    aman = re.sub(r"[^a-z0-9.-]+", "_", mentah.lower()).strip("_.")
    aman = aman[:PANJANG_MAKS_NAMA_FOLDER].strip("_.")
    if aman == "":
        return "tanpa_nama"
    return aman

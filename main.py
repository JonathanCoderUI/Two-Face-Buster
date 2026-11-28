"""Pintu masuk perintah terminal Situs Siluman."""

# File BERSAMA. Hanya memanggil fungsi modul lain, tidak berisi logika deteksi.
# Rujukan: Panduan hlm. 35-37.

import argparse
import asyncio
import csv
import sys

from siluman import config, db


def baca_url(lokasi):
    """Baca kolom url dari file CSV lalu kembalikan daftar URL-nya."""
    daftar = []
    with open(lokasi, newline="", encoding="utf-8-sig") as berkas:
        for baris in csv.DictReader(berkas):
            url = baris.get("url")
            if url == None:
                continue
            url = url.strip()
            if url == "":
                continue
            daftar.append(url)
    return daftar


def buat_pembaca_argumen():
    """Susun argumen terminal: opsi umum lalu satu subperintah per tahap."""
    pembaca = argparse.ArgumentParser(prog="main.py", description="Situs Siluman: deteksi cloaking judi online")
    pembaca.add_argument("--db", default=config.LOKASI_DB, help="lokasi database SQLite")
    pembaca.add_argument("--putaran", type=int, default=1, help="nomor putaran scan")
    subperintah = pembaca.add_subparsers(dest="perintah", required=True)

    scan = subperintah.add_parser("scan", help="kunjungi semua URL di file CSV")
    scan.add_argument("--input", required=True, help="CSV berkolom url")
    scan.add_argument("--jeda", type=float, default=config.JEDA_PER_DOMAIN, help="detik antar kunjungan ke domain yang sama")

    nilai = subperintah.add_parser("nilai", help="beri skor dan label tiap URL")
    nilai.add_argument("--model", default=None, help="model hasil perintah latih (opsional)")

    subperintah.add_parser("bukti", help="simpan tangkapan layar URL yang dicurigai")
    subperintah.add_parser("laporan", help="buat surat untuk temuan yang sudah diverifikasi")

    ekspor = subperintah.add_parser("ekspor-label", help="tulis CSV untuk dilabeli manusia")
    ekspor.add_argument("--keluar", required=True, help="lokasi CSV keluaran")

    latih = subperintah.add_parser("latih", help="latih model dari CSV berlabel")
    latih.add_argument("--data", required=True, help="CSV yang kolom label-nya sudah diisi")
    latih.add_argument("--keluar", required=True, help="lokasi file model")
    return pembaca


def jalankan_perintah(args, conn):
    """Panggil modul yang sesuai dengan subperintah yang dipilih."""
    # Impor di dalam cabang: perintah lain tetap jalan walau library modul ini belum terpasang.
    if args.perintah == "scan":
        from siluman import crawler

        daftar_url = baca_url(args.input)
        asyncio.run(crawler.scan(daftar_url, conn, args.putaran, args.jeda))
        print("Selesai memindai", len(daftar_url), "URL (putaran", str(args.putaran) + ")")
    elif args.perintah == "nilai":
        from siluman import skor

        model = None
        if args.model != None:
            from siluman import classifier

            model = classifier.muat_model(args.model)
        jumlah = skor.nilai_semua(conn, args.putaran, model)
        for label in jumlah:
            print(label.ljust(18), jumlah[label])
    elif args.perintah == "bukti":
        from siluman import bukti

        daftar_url = db.url_dicurigai(conn, args.putaran)
        asyncio.run(bukti.kumpulkan_bukti(daftar_url))
        print("Bukti dikumpulkan untuk", len(daftar_url), "URL")
    elif args.perintah == "laporan":
        from siluman import laporan

        jumlah = laporan.buat_semua(conn, args.putaran)
        print("Surat dibuat:", jumlah)
    elif args.perintah == "ekspor-label":
        from siluman import classifier

        jumlah = classifier.ekspor_untuk_label(conn, args.putaran, args.keluar)
        print("Baris diekspor:", jumlah, "->", args.keluar)
    elif args.perintah == "latih":
        from siluman import classifier

        classifier.latih_dan_evaluasi(args.data, args.keluar)
        print("Model disimpan di", args.keluar)


def main(argv=None):
    """Baca argumen terminal lalu jalankan satu tahap."""
    args = buat_pembaca_argumen().parse_args(argv)
    conn = db.buka(args.db)
    try:
        jalankan_perintah(args, conn)
    except FileNotFoundError as galat:
        print("File tidak ditemukan:", galat.filename, file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

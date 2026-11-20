# TODO per file

Daftar pekerjaan untuk setiap file di repo, disusun dari *Panduan Membangun dari Nol* dan *Rencana Kerja Tim*. Kalau ada yang berbeda, kedua dokumen itu yang berlaku.

**Cara pakai**

- Satu kotak centang bisa jadi satu issue di papan tugas. Tulis `Closes #<nomor>` di deskripsi PR supaya issue tertutup otomatis.
- Centang kotaknya lewat PR yang sama dengan PR kodenya, jangan terpisah.
- Daftar ini hanya berisi **apa** yang harus ada, bukan **bagaimana** caranya. Cara menulisnya urusan pemilik modul.
- File bersama (`siluman/db.py`, `main.py`, `tests/test_pipeline.py`, `requirements.txt`) baru boleh di-merge setelah disetujui dua anggota lain.

**Status per 14 November 2026:** kerangka sudah di `main`, semua file `.py` masih kosong. Checkpoint Minggu 1 (11 Nov) terlewat.

| Tanggal yang tidak boleh mundur | Isi |
| --- | --- |
| 11 Nov | arahan dosen sebelum scan situs asli |
| 25 Nov | laporan pertama terkirim ke admin situs |
| 9 Des | deadline semua luaran |

---

## Bersama

### `siluman/db.py` (prioritas pertama: semua modul bergantung padanya)

Rujukan: Panduan hlm. 4–7.

- [ ] Skema tiga tabel `kunjungan`, `hasil`, `laporan`, persis seperti Panduan hlm. 5, termasuk indeks `(putaran, url)`
- [ ] `buka(lokasi)`: koneksi SQLite, tabel dibuat kalau belum ada, mode WAL supaya dashboard bisa membaca saat scan berjalan
- [ ] `simpan_kunjungan(conn, k)`: HTML disimpan terkompres zlib
- [ ] `ambil_versi(conn, putaran, url)` → `{"browser": k, "googlebot": k, "dari_google": k}` dengan HTML sudah dibuka
- [ ] `simpan_hasil(conn, h)`: kolom `verifikasi` tidak boleh tertimpa
- [ ] `tandai_verifikasi(conn, putaran, url, nilai)` untuk tombol dashboard (`benar` / `salah`)
- [ ] `catat_laporan(conn, domain, status, catatan, tanggal)` untuk status surat
- [ ] `url_dicurigai(conn, putaran)` untuk perintah `bukti`
- [ ] `nama_folder(url)` untuk folder `bukti/` per URL
- [ ] Diketik satu orang, dibaca dua orang, masuk lewat PR yang di-approve dua anggota

Selesai kalau: contoh dict kunjungan di Panduan hlm. 7 bisa disimpan ke `data/contoh.db` lalu dibaca kembali lewat `ambil_versi`.

### `main.py`

Rujukan: Panduan hlm. 35–37.

- [ ] Opsi umum `--db` dan `--putaran` untuk semua subperintah
- [ ] Subperintah `scan --input --jeda`, `nilai --model`, `bukti`, `laporan`, `ekspor-label --keluar`, `latih --data --keluar`
- [ ] Modul di-import di dalam cabang tiap subperintah, supaya perintah lain tetap jalan walau library-nya belum terpasang
- [ ] Membaca kolom `url` dari CSV dan melewati baris kosong
- [ ] Tidak berisi logika deteksi, hanya memanggil fungsi modul lain

Selesai kalau: alur di Panduan hlm. 37 (scan, nilai, bukti, laporan) jalan di situs uji.

### `tests/test_pipeline.py`

- [ ] Halaman siluman tertangkap (`/cloak-ua/`, `/cloak-samaran/`, `/cloak-referer/`, `/tersembunyi/` → `hampir_pasti`)
- [ ] Halaman jujur aman (`/normal/`, `/dinamis/`, `/edukasi/`)
- [ ] Judol terbuka → `perlu_dicek`
- [ ] robots.txt dihormati (`/rahasia/` → `tidak_bisa_dicek`)
- [ ] Redirect ke situs lain tidak diikuti

### File konfigurasi

- [x] `requirements.txt`
- [x] `pytest.ini`
- [x] `.gitignore`
- [x] `.github/pull_request_template.md`
- [ ] `siluman/__init__.py`: biarkan kosong (penanda paket)
- [ ] `CLAUDE.md` tim: konteks proyek dan aturan tutor untuk Claude Code. Catatan pribadi tiap anggota masuk `CLAUDE.local.md` (tidak di-commit)

### `docs/`

- [ ] `docs/ai-prompts.md`: setiap anggota menambah satu baris untuk setiap sesi AI, di hari yang sama
- [ ] `docs/etika.md` (pemilik: Penjelajah): aturan etika, persetujuan bertiga dengan tanggal dan nama, arahan dosen (tanggal, siapa, isi pesan), catatan kejadian selama scan
- [ ] `docs/panduan.md`: ekspor panduan teknis versi belajar
- [ ] `docs/evaluasi.md` (belum ada, pemilik: Detektif, Minggu 3): catatan alarm palsu dan kandidat manual yang lolos

---

## Penjelajah

### `siluman/config.py` (Minggu 1)

Rujukan: Panduan hlm. 16–17.

- [ ] Header tiga persona: `browser`, `googlebot`, `dari_google` (browser + Referer Google)
- [ ] User-Agent browser disalin dari `chrome://version` laptop sendiri; User-Agent Googlebot dari dokumentasi crawler Google
- [ ] Urutan kunjungan persona, dengan `dari_google` lebih dulu
- [ ] Jeda per domain minimal 1 detik, maksimal 50 domain bersamaan, batas waktu, batas ukuran HTML, batas lompatan redirect, lokasi database

### `siluman/crawler.py`

Rujukan: Panduan hlm. 16–21.

- [ ] **Mg 1:** `host_dari(url)` (host tanpa `www.`) dan `situs_sama(a, b)`. Dipakai `fitur.py`, `skor.py`, `bukti.py`, jadi perubahannya wajib dikabari
- [ ] **Mg 1:** `ambil()` untuk 1 URL dengan 3 persona: redirect di situs yang sama diikuti, redirect ke situs lain hanya dicatat di `redirect_ke`, galat dicatat di `catatan` tanpa menghentikan program
- [ ] **Mg 2:** `scan(daftar_url, conn, putaran, jeda)` async: satu tugas per domain, semaphore, jeda per domain, robots.txt, fallback sertifikat SSL kedaluwarsa, cookie tidak disimpan
- [ ] **Mg 2:** uji coba 20 domain asli setelah arahan dosen, catat lamanya
- [ ] **Mg 4:** halaman selain beranda dari `sitemap.xml` dan link internal, maksimal 20 per situs; ukur waktu 1 vs 50 domain bersamaan

### `tests/test_crawler.py`

- [ ] `host_dari` dan `situs_sama`, termasuk subdomain dan URL rusak
- [ ] Server mati dicatat, tidak membuat crash
- [ ] Server lambat (`/lambat/`) dicatat `timeout`

### `scripts/coba_satu_url.py`

- [ ] Satu URL situs uji dengan 3 persona, cetak status, `redirect_ke`, dan ada tidaknya HTML

### `data/contoh_urls.csv`

- [ ] Kolom `url`, berisi 8 halaman situs uji: `/cloak-ua/1`, `/cloak-samaran/1`, `/cloak-referer/1`, `/tersembunyi/1`, `/terbuka/1`, `/normal/1`, `/dinamis/1`, `/edukasi/1`
- [ ] Satu-satunya file di `data/` yang di-commit

### Di luar repo

- [ ] **Mg 1:** 100–300 domain awal satu provinsi beserta kontak resmi, di `data/domains.csv` (tidak di-commit)

---

## Detektif

### `siluman/normalisasi.py` (Minggu 1)

- [ ] Normalisasi sesuai 6 langkah spesifikasi (NFKD, buang Mn dan Cf, huruf kecil, peta huruf mirip, rapikan spasi, rapatkan huruf berulang)
- [ ] Daftar frasa promosi
- [ ] Pencocokan frasa yang tetap kena saat digabung (`slotgacor`) atau diberi tanda hubung (`slot-gacor`), tapi tidak terpicu "slot pendaftaran PPDB"
- [ ] Nilai judol kata kunci: banyaknya frasa berbeda dibagi 6, maksimal 1

### `siluman/fitur.py`

- [ ] **Mg 1:** `ekstrak_teks(html)`: isi halaman, judul, dan meta description; script dan style dibuang (dipakai dashboard)
- [ ] **Mg 1:** `kemiripan(teks_a, teks_b)` dengan difflib atas urutan kata
- [ ] **Mg 2:** deteksi elemen tersembunyi yang berisi frasa promosi atau minimal 3 link ke situs lain
- [ ] **Mg 2:** deteksi skrip yang memeriksa asal kunjungan lalu memindahkan halaman
- [ ] **Mg 2:** deteksi nama domain tujuan redirect yang berbau judol

### `siluman/skor.py`

- [ ] Semua ambang dan poin dikumpulkan di bagian atas file
- [ ] **Mg 1:** `nilai_url(versi, model=None)` versi kata kunci → `skor, label, alasan, kemiripan, p_judol_browser, p_judol_googlebot`
- [ ] **Mg 1:** `nilai_semua(conn, putaran, model=None)` → jumlah URL per label, hasil disimpan lewat `db.simpan_hasil`
- [ ] **Mg 2:** kesembilan tanda poin sesuai tabel di Panduan hlm. 26
- [ ] **Mg 2:** label `tidak_bisa_dicek` saat versi browser atau Googlebot gagal, tidak pernah `aman`
- [ ] **Mg 3:** tinjau alarm palsu dari scan asli, setel poin dan daftar frasa lewat PR

### `siluman/classifier.py` (Minggu 4, opsional)

- [ ] `ekspor_untuk_label`, `latih_dan_evaluasi`, `muat_model` (dipanggil oleh `main.py`)
- [ ] Evaluasi dikelompokkan per domain, dibandingkan dengan metode kata kunci pada data yang sama

### `tests/test_normalisasi.py`

- [ ] 6 baris tabel Masukan → Hasil di Panduan hlm. 22
- [ ] Frasa gabung dan bertanda hubung tetap cocok
- [ ] "slot pendaftaran PPDB" tidak terpicu
- [ ] Artikel edukasi (2 frasa) bernilai di bawah 0,5

### `tests/test_fitur.py`

- [ ] Dua teks identik bernilai kemiripan 1
- [ ] `/cloak-ua/` sekitar 0,37 dan `/dinamis/` sekitar 0,85
- [ ] Meta description ikut terambil, isi script tidak
- [ ] **Mg 2:** teks tersembunyi tertangkap, menu tersembunyi biasa diabaikan, skrip pengalih tertangkap

### `tests/test_skor.py`

- [ ] Skor tiap halaman situs uji: 70 / 70 / 65 / 60 / 50 / 0 / 0 / 0
- [ ] `tidak_bisa_dicek` saat salah satu versi gagal

### `scripts/evaluasi_situs_uji.py` (Minggu 2)

- [ ] 30 halaman bertrik dan 30 halaman jujur, cetak TP, FP, FN, TN, precision, dan recall
- [ ] "Ditandai" berarti label `hampir_pasti` atau `perlu_dicek`

---

## Pelapor

### `situs_uji/app.py` (Minggu 1, dibutuhkan semua orang)

Rujukan: Panduan hlm. 12–16.

- [ ] Halaman `/normal/<n>`, `/dinamis/<n>`, `/edukasi/<n>`, `/cloak-ua/<n>`, `/cloak-samaran/<n>`, `/cloak-referer/<n>`, `/tersembunyi/<n>`, `/terbuka/<n>`, `/rahasia/<n>`, `/lambat/<n>`, dan `/robots.txt`
- [ ] Fungsi untuk menjalankan situs uji di thread terpisah pada port acak, dipakai tes
- [ ] Hanya jalan di `127.0.0.1` port 5050, semua isi judol bertanda CONTOH UJI, semua link judol berakhiran `.invalid`

### `tests/conftest.py` (Minggu 1)

- [ ] Fixture `alamat_uji` yang menyalakan situs uji sekali untuk seluruh sesi tes

### `siluman/bukti.py` (Minggu 2)

- [ ] `kumpulkan_bukti(daftar_url)` async: tangkapan layar versi `browser` dan `googlebot` dengan Playwright headless
- [ ] Semua permintaan ke situs lain diblokir sebelum terkirim
- [ ] Hasil di `bukti/<folder per URL>/browser.png` dan `googlebot.png`

### `dashboard.py` (Minggu 2, final Minggu 4)

- [ ] Pesan jelas saat database belum berisi hasil
- [ ] Angka ringkasan: URL dipindai, hampir pasti, perlu dicek, terverifikasi judol, tidak bisa dicek
- [ ] Tabel hasil dengan filter label, diurutkan dari skor tertinggi
- [ ] Detail URL: daftar alasan, teks versi browser dan Googlebot berdampingan, tangkapan layar kalau ada, peringatan kalau pengunjung dari Google dialihkan
- [ ] Tombol "Benar, ini konten judol" dan "Alarm palsu" yang mengisi kolom `verifikasi`
- [ ] Pelacakan status surat (`draf`, `terkirim`, `dibalas`, `bersih`, `eskalasi`)

### `tests/test_dashboard.py`

- [ ] Dashboard jalan tanpa data, tanpa exception
- [ ] Tombol verifikasi mengisi database

### `siluman/laporan.py` dan `siluman/templates/laporan.md.j2`

- [ ] **Mg 1:** templat surat versi pertama
- [ ] **Mg 3:** `buat_semua(conn, putaran)`: hanya temuan berlabel `hampir_pasti` atau `perlu_dicek` yang sudah diverifikasi `benar`, satu surat per domain di `laporan_keluar/<domain>.md`, status dicatat `draf`
- [ ] Nama dan email resmi tim diisi sebelum surat pertama dikirim

### `README.md` (Minggu 4)

- [ ] Masalah dalam satu paragraf, tangkapan layar dashboard situs uji, cara instal, lima perintah utama, diagram arsitektur, etika dan batasan, hasil dan akurasi, tim dan peran, link video, link `docs/ai-prompts.md`

### `.github/workflows/` (Minggu 2)

- [ ] Workflow dari templat Actions "Python application": pasang `requirements.txt` lalu jalankan `pytest` di setiap push dan PR, Python 3.13

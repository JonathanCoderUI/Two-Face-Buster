"""Dashboard Streamlit untuk meninjau temuan, memverifikasi, dan melacak status surat."""

# Pemilik: Pelapor. Rujukan: Panduan hlm. 31-33.
# Jalankan dengan: streamlit run dashboard.py

# TODO 1:
# Buka database (lokasi dari config.LOKASI_DB, bisa diganti lewat variabel SILUMAN_DB)
# dan pilih putaran scan di sidebar.
...

# TODO 2:
# Kalau belum ada hasil, tampilkan pesan yang menyuruh menjalankan scan lalu nilai.
...

# TODO 3:
# Angka ringkasan: URL dipindai, hampir pasti, perlu dicek, terverifikasi judol, tidak bisa dicek.
...

# TODO 4:
# Tabel hasil dengan filter label, diurutkan dari skor tertinggi.
...

# TODO 5:
# Detail satu URL: daftar alasan, teks versi browser dan Googlebot berdampingan
# (pakai fitur.ekstrak_teks), tangkapan layar dari bukti/ kalau ada, dan peringatan
# kalau pengunjung dari Google dialihkan.
...

# TODO 6:
# Tombol "Benar, ini konten judol" dan "Alarm palsu" yang memanggil db.tandai_verifikasi.
...

# TODO 7:
# Pelacakan laporan: tabel status surat dan formulir untuk mengubahnya lewat db.catat_laporan.
...

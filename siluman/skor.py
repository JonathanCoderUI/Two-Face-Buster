"""Menjumlahkan poin tiap kejanggalan menjadi skor, label, dan alasan."""

# Pemilik: Detektif.

from siluman.fitur import ekstrak_teks, kemiripan
from siluman.normalisasi import nilai_judol_kata_kunci

# ---- Angka yang bisa disetel (spesifikasi skor) ----
AMBANG_JUDOL = 0.5          # nilai judol minimal agar isi dianggap judol
AMBANG_SANGAT_BERBEDA = 0.5  # kemiripan di bawah ini = dua versi sangat berbeda

BATAS_HAMPIR_PASTI = 60
BATAS_PERLU_DICEK = 25

POIN_JUDOL_HANYA_GOOGLEBOT = 50
POIN_JUDOL_HANYA_DARI_GOOGLE = 50
POIN_DIALIHKAN_HANYA_TAMU_GOOGLE = 45   # Minggu 2
POIN_DOMAIN_BERBAU_JUDOL = 20           # Minggu 2
POIN_TERSEMBUNYI_KUAT = 60              # Minggu 2
POIN_TERSEMBUNYI_LEMAH = 30             # Minggu 2
POIN_JUDOL_TERLIHAT_SEMUA = 50
POIN_VERSI_SANGAT_BERBEDA = 20
POIN_SKRIP_PENGALIH = 20                # Minggu 2

LABEL_HAMPIR_PASTI = "hampir_pasti"
LABEL_PERLU_DICEK = "perlu_dicek"
LABEL_AMAN = "aman"
LABEL_TIDAK_BISA_DICEK = "tidak_bisa_dicek"


def nilai_url(versi, model=None):
    """Kembalikan dict skor, label, alasan, kemiripan, p_judol_browser, p_judol_googlebot untuk satu URL."""
    # model baru dipakai Minggu 4 (classifier); versi ini hanya kata kunci.
    k_browser = versi.get("browser")
    k_googlebot = versi.get("googlebot")
    k_dari_google = versi.get("dari_google")

    # Tanpa versi browser dan Googlebot tidak ada yang bisa dibandingkan, jadi
    # labelnya tidak_bisa_dicek, tidak pernah aman.
    if gagal_diambil(k_browser):
        return hasil_tidak_bisa_dicek("Versi browser gagal diambil: " + catatan_dari(k_browser))
    if gagal_diambil(k_googlebot):
        return hasil_tidak_bisa_dicek("Versi Googlebot gagal diambil: " + catatan_dari(k_googlebot))

    teks_browser = ekstrak_teks(k_browser.get("html"))
    teks_googlebot = ekstrak_teks(k_googlebot.get("html"))
    if teks_browser == "" and teks_googlebot == "":
        return hasil_tidak_bisa_dicek("Versi browser dan Googlebot sama-sama tanpa teks")

    judol_browser = nilai_judol_kata_kunci(teks_browser)
    judol_googlebot = nilai_judol_kata_kunci(teks_googlebot)
    judol_dari_google = None
    if not gagal_diambil(k_dari_google):
        judol_dari_google = nilai_judol_kata_kunci(ekstrak_teks(k_dari_google.get("html")))

    alasan = []

    if judol_browser >= AMBANG_JUDOL:
        # Kalau pengunjung biasa pun melihat judol, ini bukan cloaking, jadi tanda
        # "hanya untuk Googlebot/dari Google" tidak dinilai lagi.
        tambah_alasan(alasan, POIN_JUDOL_TERLIHAT_SEMUA, "Isi judol terlihat oleh semua pengunjung")
    else:
        if judol_googlebot >= AMBANG_JUDOL:
            tambah_alasan(alasan, POIN_JUDOL_HANYA_GOOGLEBOT, "Isi judol hanya muncul untuk Googlebot")
        if judol_dari_google != None and judol_dari_google >= AMBANG_JUDOL:
            tambah_alasan(alasan, POIN_JUDOL_HANYA_DARI_GOOGLE, "Isi judol hanya muncul untuk pengunjung dari Google")

    nilai_kemiripan = None
    if teks_browser != "" and teks_googlebot != "":
        nilai_kemiripan = kemiripan(teks_browser, teks_googlebot)
        if nilai_kemiripan < AMBANG_SANGAT_BERBEDA:
            persen = str(round(nilai_kemiripan * 100))
            tambah_alasan(alasan, POIN_VERSI_SANGAT_BERBEDA, "Versi Googlebot sangat berbeda dari versi browser (kemiripan " + persen + "%)")

    skor = jumlah_poin(alasan)
    return {
        "skor": skor,
        "label": label_dari_skor(skor),
        "alasan": alasan,
        "kemiripan": nilai_kemiripan,
        "p_judol_browser": judol_browser,
        "p_judol_googlebot": judol_googlebot,
    }


def gagal_diambil(kunjungan):
    """True kalau kunjungan tidak ada, galat, berstatus 4xx/5xx, atau tanpa HTML dan tanpa pengalihan."""
    if kunjungan == None:
        return True
    status = kunjungan.get("status")
    if status == None or status >= 400:
        return True
    # Tanpa HTML tapi dialihkan ke situs lain bukan kegagalan: itu tanda pengalihan (Minggu 2).
    if kunjungan.get("html") == None and kunjungan.get("redirect_ke") == None:
        return True
    return False


def catatan_dari(kunjungan):
    """Kembalikan catatan galat kunjungan untuk ditampilkan di alasan."""
    if kunjungan == None:
        return "tidak ada kunjungan"
    catatan = kunjungan.get("catatan")
    if catatan == None or catatan == "":
        return "status " + str(kunjungan.get("status"))
    else:
        return catatan


def hasil_tidak_bisa_dicek(teks_alasan):
    """Kembalikan hasil berlabel tidak_bisa_dicek dengan satu alasan."""
    return {
        "skor": 0,
        "label": LABEL_TIDAK_BISA_DICEK,
        "alasan": [{"poin": 0, "teks": teks_alasan}],
        "kemiripan": None,
        "p_judol_browser": None,
        "p_judol_googlebot": None,
    }


def tambah_alasan(alasan, poin, teks):
    """Tambahkan satu alasan berbentuk {"poin": ..., "teks": ...} ke daftar alasan."""
    alasan.append({"poin": poin, "teks": teks})


def jumlah_poin(alasan):
    """Kembalikan jumlah poin semua alasan."""
    total = 0
    for satu in alasan:
        total = total + satu["poin"]
    return total


def label_dari_skor(skor):
    """Kembalikan label hampir_pasti, perlu_dicek, atau aman sesuai batas skor."""
    if skor >= BATAS_HAMPIR_PASTI:
        return LABEL_HAMPIR_PASTI
    elif skor >= BATAS_PERLU_DICEK:
        return LABEL_PERLU_DICEK
    else:
        return LABEL_AMAN


def nilai_semua(conn, putaran, model=None):
    """Nilai semua URL di satu putaran, simpan ke tabel hasil, lalu kembalikan jumlah URL per label."""
    # TODO 4 (menunggu db.py):
    # Butuh fungsi db untuk mendaftar URL di satu putaran; fungsi itu belum ada di
    # kontrak db.py, jadi menambahkannya wajib lewat PR yang di-review dua anggota.
    # Untuk tiap URL: db.ambil_versi -> nilai_url -> db.simpan_hasil (beserta putaran,
    # url, domain, waktu), lalu hitung jumlah URL per label.
    ...

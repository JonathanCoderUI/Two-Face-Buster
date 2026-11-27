"""Menjumlahkan poin tiap kejanggalan menjadi skor, label, dan alasan."""

# Pemilik: Detektif.

import datetime

from siluman import db
from siluman.fitur import (
    cari_teks_tersembunyi,
    ekstrak_teks,
    ekstrak_teks_terlihat,
    kemiripan,
    nama_domain_berbau_judol,
    skrip_pengalih_referrer,
)
from siluman.normalisasi import nilai_judol_kata_kunci

# ---- Angka yang bisa disetel (spesifikasi skor) ----
AMBANG_JUDOL = 0.5          # nilai judol minimal agar isi dianggap judol
AMBANG_SANGAT_BERBEDA = 0.5  # kemiripan di bawah ini = dua versi sangat berbeda
MIN_FRASA_TERSEMBUNYI_KUAT = 3  # frasa promosi berbeda di elemen tersembunyi agar dihitung kuat

BATAS_HAMPIR_PASTI = 60
BATAS_PERLU_DICEK = 25

POIN_JUDOL_HANYA_GOOGLEBOT = 50
POIN_JUDOL_HANYA_DARI_GOOGLE = 50
POIN_DIALIHKAN_HANYA_TAMU_GOOGLE = 45
POIN_DOMAIN_BERBAU_JUDOL = 20
POIN_TERSEMBUNYI_KUAT = 60
POIN_TERSEMBUNYI_LEMAH = 30
POIN_JUDOL_TERLIHAT_SEMUA = 50
POIN_VERSI_SANGAT_BERBEDA = 20
POIN_SKRIP_PENGALIH = 20

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

    # Nilai judol dihitung dari teks yang terlihat saja: teks tersembunyi punya
    # tandanya sendiri, jadi tidak dihitung dua kali sebagai "isi judol terlihat".
    judol_browser = nilai_judol_kata_kunci(ekstrak_teks_terlihat(k_browser.get("html")))
    judol_googlebot = nilai_judol_kata_kunci(ekstrak_teks_terlihat(k_googlebot.get("html")))
    judol_dari_google = None
    if not gagal_diambil(k_dari_google):
        judol_dari_google = nilai_judol_kata_kunci(ekstrak_teks_terlihat(k_dari_google.get("html")))

    alasan = []

    if browser_dialihkan_ke_judol(k_browser):
        # Pengunjung biasa pun dialihkan: bukan cloaking, jadi tanda "hanya untuk
        # Googlebot/dari Google" tidak dinilai lagi.
        tambah_alasan(alasan, POIN_JUDOL_TERLIHAT_SEMUA, "Pengunjung biasa pun dialihkan ke domain berbau judol")
    elif judol_browser >= AMBANG_JUDOL:
        # Kalau pengunjung biasa pun melihat judol, ini bukan cloaking.
        tambah_alasan(alasan, POIN_JUDOL_TERLIHAT_SEMUA, "Isi judol terlihat oleh semua pengunjung")
    else:
        if judol_googlebot >= AMBANG_JUDOL:
            tambah_alasan(alasan, POIN_JUDOL_HANYA_GOOGLEBOT, "Isi judol hanya muncul untuk Googlebot")
        if judol_dari_google != None and judol_dari_google >= AMBANG_JUDOL:
            tambah_alasan(alasan, POIN_JUDOL_HANYA_DARI_GOOGLE, "Isi judol hanya muncul untuk pengunjung dari Google")

    tambah_tanda_pengalihan(alasan, k_browser, k_googlebot, k_dari_google)

    nilai_kemiripan = None
    if teks_browser != "" and teks_googlebot != "":
        nilai_kemiripan = kemiripan(teks_browser, teks_googlebot)
        if nilai_kemiripan < AMBANG_SANGAT_BERBEDA:
            persen = str(round(nilai_kemiripan * 100))
            tambah_alasan(alasan, POIN_VERSI_SANGAT_BERBEDA, "Versi Googlebot sangat berbeda dari versi browser (kemiripan " + persen + "%)")

    daftar_kunjungan = [k_browser, k_googlebot, k_dari_google]
    tambah_tanda_tersembunyi(alasan, daftar_kunjungan)
    tambah_tanda_skrip(alasan, daftar_kunjungan)

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
    # Tanpa HTML tapi dialihkan ke situs lain bukan kegagalan: itu tanda pengalihan.
    if kunjungan.get("html") == None and not dialihkan(kunjungan):
        return True
    return False


def dialihkan(kunjungan):
    """True kalau kunjungan dialihkan ke situs lain (crawler hanya mengisi redirect_ke untuk situs lain)."""
    if kunjungan == None:
        return False
    tujuan = kunjungan.get("redirect_ke")
    if tujuan == None or tujuan == "":
        return False
    return True


def browser_dialihkan_ke_judol(k_browser):
    """True kalau pengunjung biasa dialihkan ke domain yang namanya berbau judol."""
    if not dialihkan(k_browser):
        return False
    if nama_domain_berbau_judol(k_browser["redirect_ke"]):
        return True
    return False


def tambah_tanda_pengalihan(alasan, k_browser, k_googlebot, k_dari_google):
    """Tambahkan poin kalau hanya Googlebot atau pengunjung dari Google yang dialihkan ke situs lain."""
    # Kalau browser biasa pun dialihkan, itu bukan cloaking; kasus ke domain judol sudah diurus nilai_url.
    if dialihkan(k_browser):
        return
    tujuan = []
    if dialihkan(k_googlebot):
        tujuan.append(k_googlebot["redirect_ke"])
    if dialihkan(k_dari_google):
        tujuan.append(k_dari_google["redirect_ke"])
    if len(tujuan) == 0:
        return

    tambah_alasan(alasan, POIN_DIALIHKAN_HANYA_TAMU_GOOGLE, "Googlebot atau pengunjung dari Google dialihkan ke situs lain, browser biasa tidak")
    for alamat in tujuan:
        if nama_domain_berbau_judol(alamat):
            tambah_alasan(alasan, POIN_DOMAIN_BERBAU_JUDOL, "Nama domain tujuan pengalihan berbau judol")
            return


def tambah_tanda_tersembunyi(alasan, daftar_kunjungan):
    """Tambahkan poin untuk teks atau link judol di elemen tersembunyi di versi mana pun."""
    frasa_berbeda = []
    ada_temuan = False
    for kunjungan in daftar_kunjungan:
        if gagal_diambil(kunjungan) or kunjungan.get("html") == None:
            continue
        for temuan in cari_teks_tersembunyi(kunjungan["html"], kunjungan["url"]):
            ada_temuan = True
            for frasa in temuan["frasa"]:
                if frasa not in frasa_berbeda:
                    frasa_berbeda.append(frasa)

    if len(frasa_berbeda) >= MIN_FRASA_TERSEMBUNYI_KUAT:
        teks = "Teks atau link judol tersembunyi (" + str(len(frasa_berbeda)) + " frasa promosi)"
        tambah_alasan(alasan, POIN_TERSEMBUNYI_KUAT, teks)
    elif ada_temuan:
        tambah_alasan(alasan, POIN_TERSEMBUNYI_LEMAH, "Elemen tersembunyi berisi frasa promosi atau banyak link ke situs lain")


def tambah_tanda_skrip(alasan, daftar_kunjungan):
    """Tambahkan poin kalau ada skrip yang memeriksa asal kunjungan lalu memindahkan halaman."""
    for kunjungan in daftar_kunjungan:
        if gagal_diambil(kunjungan) or kunjungan.get("html") == None:
            continue
        if skrip_pengalih_referrer(kunjungan["html"]):
            tambah_alasan(alasan, POIN_SKRIP_PENGALIH, "Skrip memeriksa asal kunjungan lalu memindahkan halaman")
            return


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
    jumlah = {
        LABEL_HAMPIR_PASTI: 0,
        LABEL_PERLU_DICEK: 0,
        LABEL_AMAN: 0,
        LABEL_TIDAK_BISA_DICEK: 0,
    }
    for url in db.daftar_url(conn, putaran):
        versi = db.ambil_versi(conn, putaran, url)
        hasil = nilai_url(versi, model)
        db.simpan_hasil(
            conn,
            {
                "putaran": putaran,
                "url": url,
                "domain": domain_dari_versi(versi),
                "skor": hasil["skor"],
                "label": hasil["label"],
                "alasan": hasil["alasan"],
                "kemiripan": hasil["kemiripan"],
                "p_judol_browser": hasil["p_judol_browser"],
                "p_judol_googlebot": hasil["p_judol_googlebot"],
                "waktu": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            },
        )
        jumlah[hasil["label"]] = jumlah[hasil["label"]] + 1
    return jumlah


def domain_dari_versi(versi):
    """Kembalikan domain dari kunjungan pertama yang punya domain, atau None."""
    for persona in ["browser", "googlebot", "dari_google"]:
        kunjungan = versi.get(persona)
        if kunjungan != None and kunjungan.get("domain") != None:
            return kunjungan["domain"]
    return None

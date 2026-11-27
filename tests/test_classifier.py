"""Tes untuk classifier.py."""

# Pemilik: Detektif.

import csv
from urllib.parse import urlsplit

import pytest

from siluman import classifier, db
from siluman.fitur import ekstrak_teks_terlihat
from siluman.skor import nilai_url
from tests.helper_situs_uji import ambil_versi

HTML_CURIGA_BOT = (
    "<p>Slot gacor maxwin hari ini, bonus new member, deposit pulsa.</p>"
    '<div style="display:none">tersembunyi slot online jackpot</div>'
)
HTML_SEKOLAH = "<p>Upacara bendera rutin dilaksanakan setiap hari Senin pagi.</p>"

TEKS_JUDOL = [
    "slot gacor hari ini maxwin bonus new member",
    "daftar slot online deposit pulsa jackpot scatter",
    "pola gacor rtp live anti rungkad maxwin",
    "S1OT G4C0R M4XW1N daftar sekarang bonus",
]
TEKS_AMAN = [
    "upacara bendera setiap hari senin di lapangan sekolah",
    "pendaftaran peserta didik baru dibuka bulan juni",
    "jadwal ujian akhir semester dan rapat orang tua siswa",
    "perpustakaan tutup sementara selama masa renovasi gedung",
]


def buat_kunjungan(url, persona, html):
    """Dict satu kunjungan berkolom tabel kunjungan, tanpa galat."""
    return {
        "putaran": 1,
        "url": url,
        "domain": urlsplit(url).hostname,
        "persona": persona,
        "waktu": "2026-11-27T00:00:00",
        "status": 200,
        "url_akhir": url,
        "redirect_ke": None,
        "html": html,
        "catatan": None,
    }


def siapkan_db(tmp_path):
    """Database sementara: satu URL dicurigai dan dua URL aman."""
    conn = db.buka(str(tmp_path / "uji.db"))
    for persona in ["browser", "dari_google"]:
        db.simpan_kunjungan(conn, buat_kunjungan("https://a.sch.id/", persona, HTML_SEKOLAH))
    db.simpan_kunjungan(conn, buat_kunjungan("https://a.sch.id/", "googlebot", HTML_CURIGA_BOT))
    for url in ["https://b.sch.id/", "https://c.sch.id/"]:
        for persona in ["browser", "googlebot", "dari_google"]:
            db.simpan_kunjungan(conn, buat_kunjungan(url, persona, HTML_SEKOLAH))
    db.simpan_hasil(conn, {"putaran": 1, "url": "https://a.sch.id/", "domain": "a.sch.id", "skor": 70, "label": "hampir_pasti"})
    return conn


def baca_csv(lokasi):
    """Baca CSV hasil ekspor menjadi daftar dict."""
    with open(lokasi, newline="", encoding="utf-8-sig") as berkas:
        return list(csv.DictReader(berkas))


def test_ekspor_kolom_dan_isi(tmp_path):
    conn = siapkan_db(tmp_path)
    lokasi = str(tmp_path / "label.csv")
    jumlah = classifier.ekspor_untuk_label(conn, 1, lokasi)
    baris_semua = baca_csv(lokasi)
    assert jumlah == len(baris_semua)
    assert list(baris_semua[0].keys()) == classifier.KOLOM_CSV
    persona_ada = set()
    for baris in baris_semua:
        persona_ada.add(baris["persona"])
        assert baris["label"] == ""
    assert persona_ada == {"browser", "googlebot"}
    # URL dicurigai: versi browser dan Googlebot, dengan teks yang terlihat saja.
    teks_bot = ""
    for baris in baris_semua:
        if baris["url"] == "https://a.sch.id/" and baris["persona"] == "googlebot":
            teks_bot = baris["teks"]
    assert teks_bot == ekstrak_teks_terlihat(HTML_CURIGA_BOT)
    assert "tersembunyi" not in teks_bot


def test_ekspor_membatasi_url_aman_secara_acak(tmp_path, monkeypatch):
    conn = siapkan_db(tmp_path)
    monkeypatch.setattr(classifier, "JUMLAH_AMAN_ACAK", 1)
    lokasi = str(tmp_path / "label.csv")
    classifier.ekspor_untuk_label(conn, 1, lokasi)
    baris_semua = baca_csv(lokasi)
    daftar_url = set()
    for baris in baris_semua:
        daftar_url.add(baris["url"])
    # Satu URL dicurigai + satu dari dua URL aman, masing-masing dua persona.
    assert len(daftar_url) == 2
    assert len(baris_semua) == 4
    assert "https://a.sch.id/" in daftar_url
    # Contoh acak yang sama setiap kali, supaya hasil ekspor bisa diulang.
    classifier.ekspor_untuk_label(conn, 1, lokasi)
    assert len(baca_csv(lokasi)) == 4


def tulis_csv_berlabel(lokasi, baris_isi):
    """Tulis CSV berlabel; tiap elemen baris_isi berisi (domain, teks, label)."""
    with open(lokasi, "w", newline="", encoding="utf-8-sig") as berkas:
        penulis = csv.DictWriter(berkas, fieldnames=classifier.KOLOM_CSV)
        penulis.writeheader()
        nomor = 0
        for domain, teks, label in baris_isi:
            nomor = nomor + 1
            penulis.writerow({
                "domain": domain,
                "url": "https://" + domain + "/" + str(nomor),
                "persona": "browser",
                "label": label,
                "teks": teks,
            })


def data_latih():
    """Dua belas contoh judol dan dua belas contoh aman, tiap domain muncul dua kali."""
    baris_isi = []
    for i in range(12):
        domain = "judol" + str(i // 2) + ".sch.id"
        baris_isi.append((domain, TEKS_JUDOL[i % 4] + " halaman " + str(i), "judol"))
    for i in range(12):
        domain = "aman" + str(i // 2) + ".sch.id"
        baris_isi.append((domain, TEKS_AMAN[i % 4] + " halaman " + str(i), "aman"))
    return baris_isi


def test_latih_menyimpan_model_dan_mengembalikan_metrik(tmp_path):
    lokasi_csv = str(tmp_path / "berlabel.csv")
    lokasi_model = str(tmp_path / "model" / "judol.joblib")
    tulis_csv_berlabel(lokasi_csv, data_latih())
    hasil = classifier.latih_dan_evaluasi(lokasi_csv, lokasi_model)
    assert hasil["jumlah"] == 24
    assert (tmp_path / "model" / "judol.joblib").exists()
    for nama in ["model", "kata_kunci"]:
        assert 0.0 <= hasil[nama]["precision"] <= 1.0
        assert 0.0 <= hasil[nama]["recall"] <= 1.0
    # Data sintetis ini mudah: model yang sehat harus menangkap hampir semuanya.
    assert hasil["model"]["recall"] >= 0.9
    assert hasil["model"]["precision"] >= 0.9


def test_model_dimuat_ulang_membedakan_judol_dan_aman(tmp_path):
    lokasi_csv = str(tmp_path / "berlabel.csv")
    lokasi_model = str(tmp_path / "judol.joblib")
    tulis_csv_berlabel(lokasi_csv, data_latih())
    classifier.latih_dan_evaluasi(lokasi_csv, lokasi_model)
    model = classifier.muat_model(lokasi_model)
    p_judol = classifier.peluang_judol(model, "slot gacor maxwin bonus new member")
    p_aman = classifier.peluang_judol(model, "upacara bendera hari senin di sekolah")
    assert p_judol > 0.5
    assert p_aman < 0.5
    # Ejaan samaran dilipat dulu oleh normalisasi, jadi tetap dikenali.
    p_samaran = classifier.peluang_judol(model, "S1OT G4C0R M4XW1N b0nus new m3mb3r")
    assert p_samaran > 0.5


def test_label_kosong_dilewati(tmp_path):
    lokasi_csv = str(tmp_path / "berlabel.csv")
    baris_isi = data_latih()
    baris_isi.append(("belum.sch.id", "teks yang belum dilabeli", ""))
    tulis_csv_berlabel(lokasi_csv, baris_isi)
    hasil = classifier.latih_dan_evaluasi(lokasi_csv, str(tmp_path / "m.joblib"))
    assert hasil["jumlah"] == 24


def test_label_salah_ketik_ditolak(tmp_path):
    lokasi_csv = str(tmp_path / "berlabel.csv")
    baris_isi = data_latih()
    baris_isi.append(("typo.sch.id", "teks apa saja", "judul"))
    tulis_csv_berlabel(lokasi_csv, baris_isi)
    with pytest.raises(ValueError, match="judul"):
        classifier.latih_dan_evaluasi(lokasi_csv, str(tmp_path / "m.joblib"))


def test_satu_kelas_saja_ditolak(tmp_path):
    lokasi_csv = str(tmp_path / "berlabel.csv")
    tulis_csv_berlabel(lokasi_csv, [("a.sch.id", "slot gacor", "judol"), ("b.sch.id", "slot online", "judol")])
    with pytest.raises(ValueError):
        classifier.latih_dan_evaluasi(lokasi_csv, str(tmp_path / "m.joblib"))


def test_satu_domain_tidak_terpecah_ke_dua_lipatan():
    grup = ["a", "a", "b", "b", "c", "c", "d", "d", "e", "e"]
    lipatan = classifier.bagi_per_domain(grup, 5)
    assert len(lipatan) == 5
    domain_pernah_diuji = set()
    for indeks_latih, indeks_uji in lipatan:
        domain_uji = set()
        for i in indeks_uji:
            domain_uji.add(grup[i])
        domain_latih = set()
        for i in indeks_latih:
            domain_latih.add(grup[i])
        # Domain yang diuji tidak boleh ikut dilatih, dan hanya diuji di satu lipatan.
        assert domain_uji.isdisjoint(domain_latih)
        assert domain_uji.isdisjoint(domain_pernah_diuji)
        domain_pernah_diuji = domain_pernah_diuji | domain_uji


class ModelPalsu:
    """Pengganti model sklearn: selalu menjawab peluang judol 0,8."""

    classes_ = [0, 1]

    def predict_proba(self, daftar_teks):
        hasil = []
        for teks in daftar_teks:
            hasil.append([0.2, 0.8])
        return hasil


def test_model_hanya_mengubah_p_judol_bukan_skor(alamat_uji):
    versi = ambil_versi(alamat_uji, "/cloak-ua/1")
    tanpa_model = nilai_url(versi)
    dengan_model = nilai_url(versi, ModelPalsu())
    assert dengan_model["skor"] == tanpa_model["skor"] == 70
    assert dengan_model["label"] == tanpa_model["label"] == "hampir_pasti"
    assert dengan_model["p_judol_browser"] == 0.8
    assert dengan_model["p_judol_googlebot"] == 0.8
    # Tanpa model, kolom itu tetap berisi nilai kata kunci.
    assert tanpa_model["p_judol_googlebot"] > 0.5
    assert tanpa_model["p_judol_browser"] == 0.0

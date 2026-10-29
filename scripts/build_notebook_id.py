"""Bangun dan jalankan versi notebook berbahasa Indonesia dari kode analisis yang sama."""
import json
import os
from pathlib import Path
import sys
import tempfile

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
TEXTS = [
"""# Tarif bandara, waktu terisi, dan waktu operasi yang belum terukur

**Pertanyaan bisnis:** apakah operator taksi perlu memprioritaskan perjalanan dari JFK atau LaGuardia menuju Manhattan dibandingkan perjalanan di dalam Manhattan?

**Sumber:** NYC TLC Yellow Taxi, Januari-April 2025. Januari-Maret membentuk perbandingan awal; April menjadi pembanding waktu berikutnya. Lingkup utama memakai pembayaran kartu/tunai dan kode tarif 1/2. Lihat `docs/METODOLOGI_ID.md` untuk seluruh aturan.

**Metrik utama:** jumlah `fare_amount` dibagi jumlah jam terisi. Waktu antre, perjalanan kosong, dan biaya operasi belum tersedia untuk menghitung pendapatan bersih atau hasil satu shift penuh.

**Data mentah lengkap:** `data/raw/` berisi 17 bagian CSV perjalanan dan referensi zona. Panduan membuka: `docs/PANDUAN_DATA_MENTAH_ID.md`. Notebook ini menggunakan agregat tersimpan agar ringan; transformasi seluruh data ada pada SQL dan `scripts/analyze.py`.
""",
"""## 1. Tentukan populasi sebelum membandingkan rute

Sumber tidak memiliki ID perjalanan publik yang dijamin unik. Baris dipertahankan; tanda tangan nilai berulang tidak otomatis dihapus. Kunci referensi zona harus unik agar join tidak menggandakan baris. Waterfall menggunakan aturan pertama yang gagal agar jumlahnya kembali ke total sumber.

Perjalanan dengan pickup atau drop-off pada 9 Maret dikeluarkan karena perubahan daylight-saving time. Lihat pengecualian beserta jumlahnya di bawah. `eligible` adalah baris yang memenuhi aturan; rute penelitian merupakan bagian dari seluruh baris layak.
""",
"""## 2. Hindari perangkap rata-rata rasio

Contoh: tarif USD 20 membutuhkan 10 menit, lalu tarif USD 20 lain membutuhkan 50 menit. Rata-rata tarif per jam kedua perjalanan adalah USD 72/jam. Namun, total USD 40 selama 60 menit menghasilkan USD 40/jam. Karena itu, tarif dan menit dijumlahkan dahulu, baru dibagi.

Tabel berikut menampilkan periode, rute, jumlah perjalanan, rata-rata tarif, rata-rata durasi, tarif per jam terisi, serta batas interval. Nama kolom teknis dipertahankan agar dapat dicocokkan dengan CSV hasil dan SQL. Grafik sumber memakai label bahasa Inggris: `train` = Januari-Maret, `holdout` = April.
""",
"""## 3. Periksa April sebagai pembanding berikutnya

Definisi rute dan aturan dibekukan sebelum membandingkan April. Interval ketidakpastian berasal dari 2.000 bootstrap harian berpasangan: seluruh rute memakai pilihan hari yang sama untuk mempertahankan kondisi harian bersama.

Interval menggambarkan variasi hari dalam periode yang tersedia. Ia tidak menghilangkan perbedaan pemilihan rute atau mengukur dampak kausal perubahan penempatan taksi. Grafik jam pickup juga hanya menggambarkan perjalanan yang teramati, tanpa mengukur permintaan yang tidak terlayani.
""",
"""## 4. Uji sensitivitas batas filter

Pemeriksaan lebih longgar memakai durasi positif sampai 240 menit dan tarif dasar positif sampai USD 1.000. Aturan lainnya tetap sama. Ini menguji dua batas tersebut, bukan seluruh kemungkinan keputusan pembersihan.

Bandingkan `fare_per_occupied_hour` dengan `primary_rate`, lalu periksa `rank` dan `primary_rank`. Persentase perubahan tercatat di `rate_change_pct`.
""",
"""## 5. Nyatakan waktu yang hilang sebagai asumsi

Skenario menambahkan menit yang tidak teramati per perjalanan, terpisah untuk bandara dan kota. Asumsi awal 30 menit bandara dan 10 menit kota adalah ilustrasi, bukan hasil pengukuran.

`tarif per jam siklus = 60 x jumlah tarif dasar / (menit terisi + perjalanan x menit tambahan)`

`menit tambahan impas bandara = rata-rata tarif bandara / tarif per jam skenario kota x 60 - rata-rata menit terisi bandara`

Ambang adalah waktu tambahan saat hasil bandara menyamai pembanding kota yang dipilih. Nilai negatif berarti bandara sudah tertinggal pada nol menit tambahan. Angka tersebut tidak memasukkan biaya operasi.
""",
"""## 6. Pengukuran sebelum mengubah prioritas operasi

Ikuti `docs/EXPERIMENT_PLAN.md`: ukur waktu antre, idle, perjalanan kosong, perjalanan selesai per shift, pembayaran pengemudi, biaya operasi, dan kualitas layanan. Bandingkan kondisi operasi yang sesuai dan tetapkan keputusan sebelum melihat hasil.

Pilot yang diusulkan menggunakan pengacakan pada pengemudi, seluruh shift tetap mengikuti kelompok awal, dan analisis intention-to-treat. Data publik proyek ini belum menjalankan pilot tersebut.

**Jalankan ulang:** `python scripts/download_data.py`, `python scripts/export_raw_csv.py`, `python scripts/analyze.py`, `python -m unittest discover -s tests -v`, lalu `python scripts/build_notebook_id.py`.

Jejak sumber ada di `data/source_manifest.json`; jejak CSV lengkap ada di `data/raw_csv_manifest.json`. Setelah memahami analisis, pilih investigasi tambahan yang dapat Anda jelaskan sendiri, misalnya pemeriksaan Mei 2025.
""",
]


def main():
    nb = nbformat.read(ROOT / "notebooks/01_route_economics.ipynb", as_version=4)
    cells = [c for c in nb.cells if c.cell_type == "markdown"]
    assert len(cells) == len(TEXTS)
    for cell, text in zip(cells, TEXTS):
        cell.source = text
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
            cell.source = cell.source.replace("Ranking preserved in April:", "Urutan rute bertahan pada April:").replace("Ranking preserved under broader limits:", "Urutan rute bertahan pada filter lebih longgar:")
    with tempfile.TemporaryDirectory() as directory:
        kernel = Path(directory) / "kernels" / "taxi-indonesia"
        kernel.mkdir(parents=True)
        (kernel / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "Python (Taxi Indonesia)", "language": "python"}), encoding="utf-8")
        previous = os.environ.get("JUPYTER_PATH")
        os.environ["JUPYTER_PATH"] = directory + (os.pathsep + previous if previous else "")
        try:
            NotebookClient(nb, timeout=120, kernel_name="taxi-indonesia", resources={"metadata": {"path": str(ROOT)}}).execute()
        finally:
            if previous is None:
                os.environ.pop("JUPYTER_PATH", None)
            else:
                os.environ["JUPYTER_PATH"] = previous
    nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
    target = ROOT / "notebooks/01_route_economics_ID.ipynb"
    nbformat.write(nb, target)
    print(f"Notebook Indonesia tersimpan; enam sel kode berhasil dijalankan: {target}")


if __name__ == "__main__":
    main()

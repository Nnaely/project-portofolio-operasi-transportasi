# Airport or City? - Panduan proyek dalam bahasa Indonesia

[PDF portofolio - 8 halaman](output/pdf/Nakata_Portofolio_Data_Analyst_Airport_or_City.pdf) | [Dashboard](https://nakata-airport-or-city.vercel.app/) | [Unduh CSV lengkap](https://github.com/Nnaely/project-portofolio-operasi-transportasi/releases/download/v1.0.0/data-mentah-nyc-tlc-jan-apr-2025.zip)

## Setelah mengunduh repo

Salinan baru repo berisi kode, hasil agregat, notebook, dan dokumen PDF. CSV perjalanan lengkap tersedia pada [Releases](https://github.com/Nnaely/project-portofolio-operasi-transportasi/releases/tag/v1.0.0). Ekstrak arsip CSV di folder utama repo agar isinya masuk ke `data/raw/`. Parquet untuk menjalankan analisis dapat diambil dengan `python scripts/download_data.py`.


**Proyek portofolio Data Analyst / Business Analyst milik Nakata**

[Buka dashboard online](https://nakata-airport-or-city.vercel.app/)

Proyek ini menjawab pertanyaan: apakah operator taksi perlu meneliti strategi menunggu penumpang di bandara, atau lebih mengutamakan perjalanan di dalam Manhattan? Analisis memakai **15.168.579 catatan perjalanan NYC Yellow Taxi, Januari-April 2025**. Tarif dasar dibandingkan dengan waktu membawa penumpang, lalu waktu antre dan perjalanan kosong dimasukkan sebagai asumsi yang dapat diubah.

Hasil akhirnya adalah usulan pengukuran dan pilot operasional. Data publik belum memuat satu shift lengkap, biaya pengemudi, maupun waktu antre yang sebenarnya.

## Mulai dari sini

1. Baca [ringkasan eksekutif](reports/RINGKASAN_EKSEKUTIF_ID.pdf) untuk memahami pertanyaan, temuan, dan keputusan yang disarankan.
2. Coba dashboard: pilih April, lalu ubah asumsi waktu tambahan di kota dan bandara.
3. Buka [notebook berbahasa Indonesia](notebooks/01_route_economics_ID.ipynb) untuk mengikuti perhitungan.
4. Gunakan [panduan data mentah](docs/PANDUAN_DATA_MENTAH_ID.md) untuk membuka seluruh CSV di `data/raw/`.
5. Pelajari [metodologi](docs/METODOLOGI_ID.md), [kamus data](docs/KAMUS_DATA_ID.md), dan [rencana pilot](docs/EXPERIMENT_PLAN.md).
6. Siapkan penjelasan Anda dengan [panduan wawancara](docs/INTERVIEW_GUIDE_ID.md).

## Temuan utama

Aturan kelayakan menghasilkan **11.044.733 perjalanan**. Sebanyak **10.148.555** di antaranya termasuk tiga rute yang dibandingkan. Berikut hasil April, periode yang dipisahkan dari Januari-Maret:

| Rute April | Perjalanan | Rata-rata tarif dasar | Rata-rata menit terisi | Tarif dasar per jam terisi |
|---|---:|---:|---:|---:|
| LaGuardia ke Manhattan | 71.029 | USD 43,41 | 31,24 | USD 83,39 |
| JFK ke Manhattan | 75.303 | USD 70,17 | 53,56 | USD 78,60 |
| Manhattan ke Manhattan | 2.531.836 | USD 13,42 | 12,53 | USD 64,31 |

Urutan LaGuardia, JFK, lalu Manhattan bertahan dari Januari-Maret ke April dan pada pemeriksaan batas filter yang lebih longgar. Namun, hasilnya berubah ketika waktu tambahan diperhitungkan. Jika perjalanan kota mendapat **10 menit tambahan** dan perjalanan bandara mendapat **30 menit tambahan** per perjalanan, hasil April menjadi JFK **USD 50,38**, LaGuardia **USD 42,54**, dan kota **USD 35,76** per jam siklus yang dimodelkan. Seluruh menit tambahan tersebut adalah asumsi.

**Keputusan yang disarankan:** ukur siklus kendaraan secara lengkap sebelum menguji perubahan prioritas penempatan taksi.

## Kontrak analisis

| Komponen | Definisi |
|---|---|
| Pemangku kepentingan | Manajer operasi armada taksi hipotetis. |
| Satuan data | Satu baris sumber = satu perjalanan yang dilaporkan. Tidak tersedia ID perjalanan publik yang dijamin unik. |
| Rute | JFK ke Manhattan, LaGuardia ke Manhattan, dan Manhattan ke Manhattan. |
| Metrik | `SUM(fare_amount) / SUM(duration_minutes) * 60`, dalam USD per jam terisi. |
| Periode pembanding awal | Januari-Maret 2025, ditandai `train`. |
| Periode validasi | April 2025, ditandai `holdout`. |
| Batas keputusan | Perbandingan tarif dan waktu menunjukkan apa yang perlu diukur sebelum pilot; pendapatan bersih dan dampak kausal memerlukan data tambahan. |

## Di mana data mentahnya?

Setelah mengunduh dan mengekstrak arsip data atau menjalankan skrip sumber, semua berkas sumber dan CSV lengkap berada di **`data/raw/`**. Empat sumber Parquet diekspor menjadi **17 bagian CSV**, masing-masing maksimal 1.000.000 baris data ditambah header. `taxi_zone_lookup.csv` berisi 265 zona. CSV mempertahankan semua kolom dan semua baris, termasuk baris yang nantinya dikeluarkan oleh analisis. Penamaan, jumlah baris, dan cara membuka dijelaskan dalam panduan data mentah.

Metadata sumber resmi berada di `data/source_manifest.json`. Daftar CSV, tipe kolom, jumlah baris, ukuran, hash, dan hasil pemeriksaan ekspor berada di `data/raw_csv_manifest.json`.

## Jalankan ulang

Gunakan Python 3.12 atau lebih baru. Jalankan dari folder proyek. Sumber Parquet berukuran sekitar 257 MB; CSV memakai lebih banyak ruang. Perintah berikut mengunduh sumber, membuat CSV mentah, menjalankan analisis, dan membangun seluruh dokumen:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/export_raw_csv.py
python scripts/analyze.py
python -m unittest discover -s tests -v
python scripts/build_notebook.py
python scripts/build_notebook_id.py
python reports/build_memo.py
python reports/build_memo_id.py
python reports/build_portfolio_pdf.py
python package_project.py
```

Jika aktivasi diblokir PowerShell, gunakan `.venv\Scripts\python.exe` sebagai pengganti `python`. Pada macOS/Linux, aktivasi dilakukan dengan `source .venv/bin/activate`. Analisis tetap membaca Parquet resmi agar efisien dan konsisten; CSV disediakan untuk pemeriksaan dan pembelajaran.

Untuk membuka web dari komputer sendiri:

```text
python -m http.server 8080 --directory dashboard/dist
```

Buka `http://localhost:8080`, lalu hentikan server dengan Ctrl+C setelah selesai. Dashboard juga bisa dibuka langsung melalui `dashboard/dist/index.html`.

## Peta berkas

| Lokasi | Isi |
|---|---|
| `data/raw/` | Empat Parquet resmi, 17 CSV perjalanan lengkap, dan CSV referensi zona. |
| `data/raw_csv_manifest.json` | Jejak ekspor CSV dan pemeriksaannya. |
| `data/processed/` | Database analisis lokal. |
| `scripts/` | Pengunduhan, ekspor CSV, analisis, dan pembuatan notebook. |
| `sql/` | Aturan kelayakan, pengelompokan rute, dan pertanyaan bisnis. |
| `outputs/` | Tabel hasil, grafik, metrik, dan laporan kualitas. |
| `notebooks/01_route_economics_ID.ipynb` | Penjelasan analisis dalam bahasa Indonesia dengan keluaran yang sudah dijalankan. |
| `docs/` | Metodologi, kamus data, panduan data mentah, pilot, wawancara, hosting, dan verifikasi. |
| `reports/RINGKASAN_EKSEKUTIF_ID.pdf` | Ringkasan keputusan dalam bahasa Indonesia. |
| `dashboard/dist/` | Web beserta unduhan publik. |

ZIP portofolio berisi kode, dokumentasi, notebook, dan hasil agregat. Data mentah tersedia melalui Releases dan dapat ditempatkan di `data/raw/` dan dapat dibuat ulang dengan dua perintah sumber di atas. Data mentah dan database lokal tidak dimasukkan ke ZIP portofolio yang diunduh dari web.

Paket terpisah **`taxi-shift-economics-lengkap.zip`** menyertakan seluruh 17 CSV perjalanan dan CSV zona di dalam `taxi-shift-economics/data/raw/`, beserta dokumentasi Indonesia. Gunakan paket ini jika ingin memindahkan seluruh bahan belajar. Paket ini dapat dibuat ulang dengan `python package_project.py --include-raw-csv`.

## Menggunakan proyek ini untuk melamar

Tunjukkan alasan memilih metrik, penyebut yang digunakan, aturan kelayakan, dan mengapa April dipisahkan. Jalankan ulang serta lakukan investigasi tambahan yang Anda pahami. Catat kontribusi Anda dan jelaskan bantuan AI secara jujur bila ditanya. Jangan mencantumkan peningkatan laba atau penghematan yang belum diukur.

Sumber: [NYC TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), [kamus resmi Yellow Taxi](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf), dan [atribusi dalam bahasa Indonesia](ATRIBUSI_ID.md).

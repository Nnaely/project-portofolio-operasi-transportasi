# Membuka dan memahami data mentah

CSV lengkap tersedia pada [Releases](https://github.com/Nnaely/project-portofolio-operasi-transportasi/releases/tag/v1.0.0). Unduh dan ekstrak arsip di folder utama repo, atau jalankan dua skrip pada bagian akhir panduan.

## Lokasi dan isi

Data berada di **`data/raw/`**, di dalam folder proyek `taxi-shift-economics`. File CSV perjalanan merupakan ekspor lengkap dari empat berkas Parquet resmi NYC TLC. Tidak ada filter tanggal, pembuangan pencilan, deduplikasi, perubahan tarif, penggabungan zona, atau agregasi saat ekspor. Karena itu, Anda tetap bisa menemukan nilai kosong, tarif negatif, dan tanggal yang tidak sesuai bulan berkas.

| Bulan berkas sumber | Total baris perjalanan | Bagian CSV |
|---|---:|---:|
| Januari 2025 | 3.475.226 | 4 |
| Februari 2025 | 3.577.543 | 4 |
| Maret 2025 | 4.145.257 | 5 |
| April 2025 | 3.970.553 | 4 |
| **Total** | **15.168.579** | **17** |

`taxi_zone_lookup.csv` merupakan referensi 265 zona, sehingga jumlah seluruh CSV di folder utama adalah 18. Referensi zona tidak dihitung sebagai baris perjalanan.

Contoh nama: `yellow_tripdata_2025-01_part01.csv`, `yellow_tripdata_2025-01_part02.csv`, hingga bagian terakhir bulan tersebut. Bagian 01 memuat satu juta baris pertama, bagian 02 memuat satu juta baris berikutnya. Bagian terakhir memuat sisanya. Setiap bagian mempunyai header sendiri. Pembagian mengikuti urutan baris berkas sumber; tidak berarti data sudah diurutkan berdasarkan tanggal.

File Parquet tetap tersedia sebagai sumber analisis. Folder `_preserved/`, bila ada, menyimpan salinan file lokal sebelum pemulihan sumber dan tidak menjadi input analisis maupun ekspor. Jangan memasukkan isinya saat menggabungkan data.

## Membuka di Excel

Satu lembar Excel dibatasi 1.048.576 baris termasuk header. Setiap bagian dibatasi satu juta baris data agar seluruh bagian muat. File tetap cukup besar, sehingga proses impor dapat memerlukan waktu dan memori.

1. Buka Excel, pilih **Data > From Text/CSV** atau **Dari Teks/CSV**.
2. Pilih satu file `..._part01.csv`.
3. Pilih encoding **UTF-8**, pemisah **koma**, dan periksa pratinjau kolom.
4. Gunakan **Transform Data** bila Excel membaca angka desimal atau tanggal sebagai teks. Nilai angka dalam CSV memakai titik sebagai pemisah desimal. Pada Power Query, gunakan **Change Type > Using Locale > English (United States)** untuk angka desimal jika diperlukan.
5. Muat bagian tersebut ke lembar. Buka bagian lain melalui workbook atau lembar terpisah. Jika ingin menganalisis seluruh 15,17 juta baris sekaligus, gunakan Python, DuckDB, atau koneksi Power Query/Data Model.

Anda juga bisa membukanya di editor teks, tetapi jangan menyimpan ulang CSV mentah melalui Excel setelah mengubah format. Simpan hasil belajar sebagai file baru di folder terpisah agar sumber tetap utuh.

## Format CSV

- Encoding UTF-8; pemisah kolom koma; desimal memakai titik.
- Baris pertama berisi nama kolom asli dari sumber. Nama kolom dipertahankan agar cocok dengan SQL dan kamus resmi.
- Nilai kosong tanpa kutip mewakili nilai hilang. String kosong, jika ada pada sumber, menggunakan kutip.
- Timestamp mengikuti waktu yang dicatat sumber, tanpa konversi ke WIB. Tanggal di luar bulan nama berkas tetap dipertahankan.
- Angka tarif menggunakan USD; jarak menggunakan mil; arti kode mengikuti kamus sumber.
- CSV menyimpan representasi teks dari nilai. Tipe data asli per bulan tercatat di manifest ekspor agar dapat dibaca ulang secara tepat.

## Membaca sedikit demi sedikit dengan Python

```python
from pathlib import Path
import pandas as pd

raw = Path('data/raw')  # jalankan dari folder proyek
file = raw / 'yellow_tripdata_2025-01_part01.csv'

# Untuk melihat contoh, bukan menganggapnya sebagai keseluruhan dataset.
contoh = pd.read_csv(file, nrows=20)
print(contoh.to_string(index=False))

# Untuk membaca seluruh bagian tanpa memuat semuanya ke memori sekaligus.
for potongan in pd.read_csv(file, chunksize=100_000):
    print(len(potongan))
```

## Memeriksa seluruh bagian dengan SQL

Contoh berikut memakai DuckDB dan hanya membaca berkas perjalanan:

```python
import duckdb

con = duckdb.connect()
jumlah = con.execute("""
    SELECT count(*)
    FROM read_csv_auto('data/raw/yellow_tripdata_2025-*_part*.csv',
                       union_by_name=true, all_varchar=true)
""").fetchone()[0]
print(jumlah)  # 15168579
```

`all_varchar=true` mempertahankan semua kolom sebagai teks untuk inspeksi awal dan menghindari inferensi tipe yang berbeda antarbagiannya. Untuk perhitungan, lakukan konversi tipe secara eksplisit memakai `sources[].columns` pada manifest; jangan menjumlahkan angka yang masih berupa teks.

## Jejak asal dan pemeriksaan

`data/source_manifest.json` mencatat URL, jumlah baris, ukuran, dan SHA-256 berkas resmi. `data/raw_csv_manifest.json` mencatat sumber tiap bagian, rentang baris sumber, jumlah baris, ukuran, tipe kolom asli, dan SHA-256 CSV.

Setiap bagian dibaca ulang dengan tipe data sumber. Pemeriksaan mencocokkan header, jumlah baris, serta jumlah fingerprint hash seluruh nilai dalam baris dengan potongan Parquet yang sama. Ini pemeriksaan integritas praktis; fingerprint hash tetap mempunyai kemungkinan benturan. Tidak ada sampel baris yang digunakan sebagai pengganti ekspor lengkap.

Untuk membuat ulang CSV:

```text
python scripts/download_data.py
python scripts/export_raw_csv.py
```

Ekspor berhenti jika sumber tidak cocok dengan hash studi atau CSV yang ada telah berubah dari hash ekspor sebelumnya. Tinjau dan simpan salinan perubahan Anda sebelum mencoba lagi.

Sumber: [NYC TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). Batas lembar: [spesifikasi Excel dari Microsoft](https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3).

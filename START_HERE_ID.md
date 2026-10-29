# Cara memakai proyek ini untuk portofolio

*Documentation by Nakata - Making this study easier to understand.*

## Inti proyek

**Airport or City?** menilai perbandingan tarif dasar perjalanan bandara dan perjalanan dalam Manhattan dengan memperhitungkan durasi. Pertanyaan bisnisnya adalah apakah keuntungan tarif yang tampak besar masih bertahan ketika waktu antre, menunggu penumpang, dan perjalanan kosong ikut diperhitungkan.

Data berasal dari NYC TLC, Januari–April 2025. Ada 15.168.579 catatan perjalanan mentah, lalu populasi dipersempit dengan aturan yang tercatat. Proyek ini relevan untuk menunjukkan cara berpikir Data Analyst / Business Analyst di bidang mobilitas, marketplace, logistik, atau operasi. Angkanya tidak langsung mewakili Indonesia.

## Urutan membuka

Panduan utama: [README_ID.md](README_ID.md). Untuk membuka seluruh data mentah dalam CSV, baca [panduan data mentah](docs/PANDUAN_DATA_MENTAH_ID.md). Dokumentasi analisis tersedia dalam [metodologi](docs/METODOLOGI_ID.md), [kamus data](docs/KAMUS_DATA_ID.md), dan [catatan verifikasi](docs/VERIFIKASI_ID.md).

1. Baca `reports/RINGKASAN_EKSEKUTIF_ID.pdf`. Dalam tiga halaman, pahami keputusan, bukti, dan batas analisisnya.
2. Buka `dashboard/dist/index.html` di browser. Ubah periode, lalu ubah asumsi menit tambahan di bandara dan kota. Perhatikan bagaimana peringkat bisa berubah tanpa mengubah tarif yang diamati.
3. Baca `notebooks/01_route_economics_ID.ipynb`. Ini jembatan dari temuan bisnis ke perhitungan.
4. Periksa `sql/01_trip_mart.sql` dan `outputs/quality_report.json`. Anda perlu mampu menjelaskan mengapa suatu baris masuk atau keluar dari sampel.
5. Jalankan ulang analisis mengikuti `README_ID.md`. Cocokkan hasil Anda dengan tabel yang disertakan.

Dashboard online: **https://nakata-airport-or-city.vercel.app/**. Untuk memperbaruinya, lihat [panduan hosting](docs/HOSTING_ID.md). Paket web tersendiri disiapkan dalam `airport-or-city-web.zip`.

## Hal yang perlu benar-benar Anda kuasai

- Mengapa `SUM(fare) / SUM(minutes)` berbeda dari `AVG(fare / minutes)`.
- Mengapa total tagihan penumpang tidak sama dengan pendapatan bersih pengemudi.
- Mengapa waktu tempuh saat membawa penumpang belum cukup untuk menilai satu shift.
- Mengapa April dipisahkan dari Januari–Maret.
- Apa yang dijelaskan interval bootstrap, dan apa yang tetap tidak terukur.
- Mengapa data tanpa ID perjalanan tidak boleh sembarang dihapus sebagai duplikat.
- Bagaimana perubahan jam musim panas memengaruhi durasi dari timestamp tanpa zona waktu.

## Menyiapkan portofolio yang menjadi milik Anda

Paket ini adalah bahan kerja lengkap. Sebelum mencantumkannya sebagai proyek Anda, jalankan ulang, baca SQL, dan lakukan satu investigasi tambahan yang dapat Anda jelaskan sendiri. Catat keputusan analisis dan perubahan yang Anda buat. Bila ditanya tentang proses pengerjaan, jelaskan bantuan AI dan kontribusi Anda secara jujur.

Pilih satu perluasan yang tidak merusak ruang lingkup awal: validasi pada Mei 2025, perbandingan hari kerja dengan akhir pekan, atau interval dengan resampling blok mingguan. Simpan hasil awal sebagai pembanding. Jangan hanya mengganti warna dashboard atau menambahkan model tanpa keputusan yang jelas.

Untuk GitHub, gunakan isi ZIP sebagai repository. Jangan mengunggah `data/raw`, database lokal, atau identitas hosting pribadi. README sudah menyediakan pintu masuk bagi reviewer, dan `.gitignore` menghindari file lokal yang besar.

Judul portofolio yang bisa dipakai: **Airport or City? An Analysis of NYC Taxi Fare Productivity and Unobserved Time**.

Contoh deskripsi singkat, setelah Anda memahami dan menjalankan ulang proyek:

> Menganalisis 15,17 juta catatan perjalanan NYC Yellow Taxi dengan Python dan SQL untuk membandingkan tarif dasar per jam terisi pada perjalanan bandara dan dalam kota. Menyusun pemeriksaan kualitas data, validasi periode April, interval bootstrap per hari, serta skenario waktu tambahan sebagai dasar rancangan pengukuran operasional.

Hindari menulis bahwa proyek ini meningkatkan profit, menurunkan biaya, atau dipakai perusahaan: pilot belum dijalankan. Panduan wawancara yang lebih terperinci tersedia di `docs/INTERVIEW_GUIDE_ID.md`.

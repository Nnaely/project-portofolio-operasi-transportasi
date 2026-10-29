# Rencana validasi: apakah strategi menuju bandara layak diuji?

*Documentation by Nakata - Making this study easier to understand.*

**Status: usulan. Belum ada pilot, pendapatan tambahan, atau penghematan yang diukur.** Analisis publik hanya merekam perjalanan dengan penumpang. Keputusan operasional memerlukan waktu antre, perjalanan kosong, permintaan, dan biaya yang belum tersedia.

## Tahap 1 — ukur denominator yang hilang

Sebelum mengacak intervensi, kumpulkan log dari pengemudi yang bersedia mengikuti studi: mulai/akhir shift, waktu tersedia, perjalanan kosong, masuk/keluar antrean, pickup/drop-off, istirahat, seluruh tarif, dan biaya operasi. Gunakan ID pengemudi tersamarkan untuk analisis. Tidak ada ID pengemudi dalam data publik proyek ini.

Tetapkan kapan waktu termasuk **jam bertugas**: seluruh waktu tersedia untuk melayani penumpang, termasuk antre dan mencari/menjemput penumpang; istirahat pribadi hanya dikeluarkan melalui aturan yang dibekukan sebelum studi. Rekonsiliasikan total waktu supaya idle time tidak hilang. Laporkan bagian shift dengan log tidak lengkap.

Bandingkan distribusi waktu kosong yang terukur dengan ambang impas skenario. Jika waktu kosong bandara biasanya melewati ambang tersebut, hipotesis manfaat strategi bandara melemah. Ini masih validasi pengukuran, belum bukti kausal.

## Tahap 2 — pilot rekomendasi yang dapat dibandingkan

| Komponen | Rancangan yang disiapkan sebelum peluncuran |
|---|---|
| Keputusan bisnis | Apakah rekomendasi lokasi menunggu meningkatkan produktivitas tarif dasar per jam bertugas dengan biaya dan kualitas layanan yang dapat diterima? |
| Pemilik | Fleet Operations memutuskan perluasan; analyst menjaga pengukuran; koordinator pengemudi memantau pelaksanaan; petugas layanan memantau keluhan. |
| Intervensi | Rekomendasi staging yang menggabungkan waktu kosong yang benar-benar terukur dan informasi operasi yang tersedia saat itu. Aturan awal dibekukan; pengemudi tetap dapat menolak rekomendasi. |
| Unit pengacakan | Pengemudi, dengan seluruh shift seorang pengemudi tetap pada kelompok yang sama selama pilot agar pembelajaran tidak berpindah antarkelompok. |
| Stratifikasi | Pola jam kerja, produktivitas baseline, dan proporsi perjalanan bandara sebelum pilot. |
| Pembanding | Praktik pemilihan lokasi biasa pada kalender yang sama, dengan logging yang sama. |
| Analisis | Intention-to-treat: hasil mengikuti kelompok penugasan awal, bukan hanya shift yang mematuhi rekomendasi. Inferensi berkelompok pada pengemudi. |

Rekomendasi hanya disampaikan ketika kendaraan berhenti dan hanya pada lokasi antre yang diizinkan. Jangan meminta pengemudi menolak penumpang atau tujuan tertentu demi memenuhi kategori analisis. Outcome mencakup **seluruh perjalanan dan seluruh waktu bertugas**, bukan hanya rute bandara–Manhattan yang menguntungkan.

## Outcome dan guardrail

**Outcome utama: jumlah tarif dasar / jumlah jam bertugas.** Hitung rasio jumlah tarif terhadap jumlah jam, dengan interval ketidakpastian yang menghormati pengelompokan pengemudi. Tampilkan juga distribusi hasil per pengemudi agar peningkatan rata-rata tidak menyembunyikan kerugian pada sebagian peserta. Metrik ini tetap bukan pendapatan bersih.

| Guardrail | Definisi dan alasan |
|---|---|
| Biaya per jam bertugas | Bahan bakar/energi, tol yang tidak diganti, dan biaya tambahan lain. Produktivitas tarif dapat naik sementara biaya memburuk. |
| Jarak kosong | Mil tanpa penumpang / seluruh mil. Menguji apakah rekomendasi menambah perjalanan yang tidak menghasilkan tarif. |
| Antrean | Distribusi waktu antre dan kepadatan staging. Banyak pengemudi menuju tempat sama dapat menghapus manfaat. |
| Pelayanan | Keluhan, penolakan perjalanan, waktu tunggu penumpang jika tersedia, dan layanan di area yang ditinggalkan. |
| Beban dan keselamatan | Durasi shift, istirahat, kejadian keselamatan, serta gangguan saat berkendara. |
| Kelengkapan log | Proporsi menit dan perjalanan yang tercatat; audit apakah kehilangan data berbeda antarkelompok. |

Jika tujuan akhir adalah laba, ukur seluruh komponen pendapatan dan biaya secara terpisah sebelum mendefinisikan outcome laba. Jangan mengubah `total_amount` publik menjadi laba dengan mengurangi perkiraan biaya yang tidak terverifikasi.

## Ukuran sampel dan keputusan sebelum melihat hasil

Tetapkan perubahan minimum yang bernilai bisnis, batas kerugian guardrail, tingkat signifikansi, dan target power bersama pemilik operasi. Gunakan variasi hasil antarpengemudi serta korelasi antarshift dari tahap pengukuran untuk memperkirakan kebutuhan pengemudi dan shift. Jutaan perjalanan publik tidak menentukan kebutuhan sampel pilot secara otomatis.

Durasi mengikuti kebutuhan sampel dan cakupan pola weekday/weekend, bukan angka minggu yang dipilih sembarang. Semua shift yang terdaftar diselesaikan sebelum pembekuan; sediakan tenggang untuk pelaporan tarif/biaya yang terlambat. Tetapkan perlakuan shift putus, pindah kelompok, dan log hilang di awal.

- **Perluas:** interval manfaat memenuhi ambang minimum yang disepakati, biaya dapat diterima, dan seluruh guardrail lolos.
- **Hentikan atau jangan perluas:** batas keselamatan/layanan terlanggar atau terdapat kerugian sesuai aturan penghentian yang sudah ditetapkan.
- **Belum konklusif:** interval masih mencakup manfaat yang terlalu kecil dan manfaat yang layak. Jangan menyebutnya berhasil; rencanakan pengukuran berikutnya secara terpisah.

Catat efek antarkelompok: pengemudi berbagi antrean dan permintaan, sehingga satu rekomendasi dapat memengaruhi pembanding. Jika pengaruh ini besar, evaluasi desain pengacakan kelompok operasional/waktu dengan bantuan pemilik operasi sebelum meluncurkan pilot.

Analisis Jan–Apr 2025 pada portofolio ini tidak menjalankan tahapan tersebut. Ia menyiapkan alasan pengukuran, metrik, dan hipotesis yang bisa diuji.

# Menerbitkan dashboard di Vercel

*Documentation by Nakata - Making this study easier to understand.*

Alamat produksi: **https://nakata-airport-or-city.vercel.app/**. Proyek Vercel: `nakata-airport-or-city`. Tanda tangan kecil **Nakata** terletak di footer.

Dashboard ini berupa HTML, CSS, dan JavaScript statis. Angka analisis sudah berada di `data.js`; server Python, database, akun ChatGPT, dan unduhan data mentah tidak diperlukan oleh pengunjung.

## Paket yang disiapkan

`airport-or-city-web.zip` berisi `dist/`, `vercel.json`, dan `.vercelignore`. Ekstrak ZIP sebelum digunakan. Paket berisi dashboard, memo PDF, dan ZIP proyek analisis yang dapat diunduh pengunjung. Identitas hosting lama dan folder Git tidak disertakan.

## Pengaturan Vercel

Gunakan folder hasil ekstraksi sebagai root proyek. Jika menggunakan repository proyek analisis lengkap, gunakan `dashboard` sebagai Root Directory.

| Pengaturan | Nilai |
|---|---|
| Framework Preset | Other |
| Build Command | Kosong |
| Install Command | Kosong |
| Output Directory | dist |
| Environment Variables | Tidak diperlukan |

Pengaturan ini sudah dinyatakan dalam `vercel.json`. Untuk pembaruan, gunakan proyek Vercel yang sama: `nakata-airport-or-city`. Paket ZIP tidak menyimpan kredensial atau sesi login.

Setelah setiap pembaruan, periksa URL produksi: halaman dapat dibuka oleh pengunjung yang tidak login, pilihan periode dan penggeser asumsi berfungsi, serta memo PDF dan ZIP proyek dapat diunduh.

Dokumentasi resmi: [konfigurasi Vercel](https://vercel.com/docs/project-configuration/vercel-json) dan [alamat deployment](https://vercel.com/docs/deployments/generated-urls).

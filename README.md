# 🛍️ Implementasi Pipeline Data Engineering dan Business Intelligence (Studi Kasus: E-Commerce Erigo Store)

Halo! 👋 Selamat datang di repositori proyek analisis data saya. 

Proyek ini disusun sebagai bagian dari **penelitian dan portofolio Data Engineering serta Business Intelligence**, dengan mengaplikasikan konsep-konsep akademis ke dalam permasalahan *real-world*. Penelitian ini mengambil studi kasus pada Erigo Store, salah satu *brand fashion* lokal terbesar di Indonesia, untuk menganalisis strategi penetapan harga (*pricing strategy*), kedalaman diskon, dan ketersediaan stok produk mereka.

Seluruh proses dalam penelitian ini—mulai dari tahap ekstraksi data mentah (*scraping*), pemrosesan dan pembersihan data (*data engineering*), hingga tahapan visualisasi akhir (*Business Intelligence*)—dikerjakan secara *end-to-end*.

## 🚀 Tahapan Penelitian

Implementasi dalam proyek ini dibagi menjadi beberapa tahapan sistematis:

1. **Tahap 1: Ekstraksi Data / Scraping (`scraper.py`)** 
   Skrip Python dikembangkan untuk melakukan ekstraksi data secara langsung dari *endpoint* JSON publik Shopify. Metode ini dipilih karena lebih efisien dan ramah terhadap *server* dibandingkan menggunakan otomatisasi *browser* (seperti Selenium). Skrip ini juga telah dilengkapi dengan *retry logic* dan pengatur waktu jeda (*delay*) untuk memastikan proses ekstraksi berjalan aman dan etis.
   
2. **Tahap 2: Data Cleaning & Engineering (`02_data_engineering.py`)**
   Data mentah hasil *scraping* diproses lebih lanjut untuk mengatasi berbagai inkonsistensi. Pada tahap ini, dilakukan penanganan data yang kosong (imputasi kategori berdasarkan nama produk), koreksi anomali harga, serta pembentukan fitur-fitur baru (*feature engineering*) seperti perhitungan persentase diskon dan identifikasi produk kolaborasi (misal: edisi JKT48, MPL).
   
3. **Tahap 3: Penyimpanan Data Terstruktur (`erigo_store.db`)**
   Untuk memfasilitasi proses *query* dan integrasi dengan perangkat lunak *Business Intelligence*, data yang telah dibersihkan disimpan ke dalam basis data SQLite lokal dengan skema yang telah dinormalisasi.
   
4. **Tahap 4 & 5: Visualisasi (Tableau) dan Data Science**
   *(Catatan: Tahapan ini masih dalam proses pengerjaan. Rencana implementasi selanjutnya mencakup pengembangan dasbor interaktif menggunakan Tableau dan penerapan algoritma clustering untuk segmentasi harga).*

## 📂 Struktur Repositori

```text
├── scraper.py                 # Skrip ekstraksi data JSON dari Shopify
├── 02_data_engineering.py     # Skrip ETL (Extract, Transform, Load)
├── requirements.txt           # Daftar pustaka (library) Python yang digunakan
├── .gitignore                 # Pengecualian file mentah (raw) dan cache
├── erigo_store.db             # Basis data SQLite berisi data bersih
└── erigo_*_clean.csv          # File CSV siap pakai untuk visualisasi di Tableau
```

## 📊 Temuan Awal (Preliminary Insights)

Berdasarkan dataset terakhir yang berhasil dikumpulkan (**309 produk unik dan 1.623 varian**), terdapat beberapa temuan awal yang signifikan:
- **Strategi Diskon Agresif:** Mayoritas produk (95.5%) dalam katalog saat ini sedang dalam masa promosi/diskon.
- **Rata-rata Potongan Harga:** Analisis menunjukkan bahwa rata-rata kedalaman diskon berada pada angka **43.2%**.
- **Segmentasi Harga Dominan:** Hampir 58% dari total produk berada pada rentang harga kelas menengah (Rp100.000 - Rp200.000).
- **Perlakuan Khusus Produk Kolaborasi:** Terdapat indikasi bahwa produk-produk kolaborasi (seperti edisi JKT48 atau M6) memiliki strategi penetapan harga dan pengelolaan stok yang berbeda dibandingkan produk reguler.

## 🛠️ Panduan Replikasi (Cara Menjalankan Kode)

Untuk mereplikasi tahapan dalam proyek ini pada lingkungan lokal Anda:

1. Lakukan *clone* pada repositori ini:
   ```bash
   git clone https://github.com/JonathanMangiring/erigo-data-pipeline.git
   cd erigo-data-pipeline
   ```
2. Instalasi pustaka pendukung:
   ```bash
   pip install -r requirements.txt
   ```
3. Eksekusi skrip secara berurutan:
   ```bash
   # 1. Ekstraksi data terbaru (Scraping)
   python scraper.py

   # 2. Pembersihan data dan penyimpanan ke basis data
   python 02_data_engineering.py
   ```

---
*Proyek ini disusun sepenuhnya untuk tujuan akademis, riset, dan portofolio profesional.* Apabila terdapat pertanyaan, masukan, atau ruang untuk diskusi terkait metodologi data yang digunakan, silakan terhubung dengan saya.

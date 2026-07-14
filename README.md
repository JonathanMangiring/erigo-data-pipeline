# 🛍️ E-Commerce Data Pipeline & Analytics (Erigo Store)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Manipulasi_Data-150458.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)
![Tableau](https://img.shields.io/badge/Tableau-Business_Intelligence-E97627.svg)
![Status](https://img.shields.io/badge/Status-Dalam_Pengembangan-brightgreen.svg)

Sebuah **proyek portofolio End-to-End Data Engineering dan Business Intelligence** yang menganalisis data katalog produk *e-commerce* dari Erigo Store (salah satu *brand fashion* terbesar di Indonesia). Proyek ini mendemonstrasikan siklus hidup data secara lengkap: mulai dari ekstraksi data mentah (Scraping), penyimpanan terstruktur (SQLite), hingga wawasan bisnis yang dapat ditindaklanjuti (Tableau).

## 🚀 Gambaran Proyek

Tujuan dari proyek ini adalah membangun *pipeline* yang mengotomatisasi pengumpulan, pembersihan, dan analisis data katalog *e-commerce* untuk menjawab pertanyaan bisnis utama seperti strategi harga, kedalaman diskon, risiko kehabisan stok (*stock-out*), dan kategorisasi produk.

### 🏗️ Arsitektur Pipeline

1. **Pengumpulan Data (Scraping):** *Scraper* Python kustom yang berinteraksi dengan *endpoint* publik `/products.json` milik Shopify. Dilengkapi dengan logika *retry*, *exponential backoff*, dan *pagination*.
2. **Data Engineering (ETL):** Pembersihan anomali, penanganan nilai yang kosong (menyimpulkan kategori dari judul produk), dan pengayaan fitur (menghitung persentase diskon, mendeteksi produk kolaborasi seperti JKT48/MPL).
3. **Penyimpanan Data:** Menyusun data yang telah diratakan (*flattened*) ke dalam *database* relasional (`SQLite`) dengan tabel-tabel yang sudah dinormalisasi.
4. **Business Intelligence:** *Dashboard* interaktif Tableau untuk memvisualisasikan kesehatan katalog, segmentasi harga, dan risiko stok. *(Sedang Dikerjakan)*
5. **Data Science:** *Clustering* harga dan analisis teks pada konvensi penamaan produk. *(Segera Hadir)*

## 📂 Struktur Repositori

```text
├── scraper.py                 # Tahap 1: Python scraper (Shopify JSON endpoint)
├── 02_data_engineering.py     # Tahap 2: Pembersihan data, pengayaan & ekspor SQLite
├── requirements.txt           # Dependensi Python
├── .gitignore                 # Mengabaikan file mentah yang besar dan cache
├── erigo_store.db             # Output: SQLite Database (Data Bersih)
└── erigo_*_clean.csv          # Output: CSV Bersih yang siap digunakan untuk Tableau
```

## 📊 Temuan Utama (Data Awal)

Dari hasil ekstraksi data terbaru yang mencakup **309 produk unik dan 1.623 varian**:
- **Pemberian Diskon yang Agresif:** 95.5% dari katalog saat ini sedang diskon.
- **Rata-rata Kedalaman Diskon:** Rata-rata potongan harga di seluruh barang diskon adalah **43.2%**.
- **Segmentasi Harga:** *Brand* ini sangat mendominasi segmen "Menengah" (Rp100rb - Rp200rb), yang mencakup ~58% dari seluruh katalog.
- **Kolaborasi Khusus:** Berhasil mendeteksi dan memisahkan item kolaborasi khusus (contoh: JKT48, M6, MPL) yang menunjukkan perilaku harga yang berbeda.

## 🛠️ Cara Menjalankan

1. *Clone* repositori ini:
   ```bash
   git clone https://github.com/JonathanMangiring/erigo-data-pipeline.git
   cd erigo-data-pipeline
   ```
2. *Install dependensi*:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan *pipeline*:
   ```bash
   # Langkah 1: Kumpulkan data mentah
   python scraper.py

   # Langkah 2: Bersihkan dan muat ke Database
   python 02_data_engineering.py
   ```

## 👨‍💻 Penulis
Dibangun sebagai karya portofolio Data Engineering & Analytics. Mari terhubung untuk berdiskusi seputar data!

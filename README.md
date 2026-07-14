# 🛍️ E-Commerce Data Pipeline (Studi Kasus: Erigo Store)

Halo! 👋 Selamat datang di repository project data analisisku. 

Project ini aku buat sebagai **portfolio Data Engineering dan Business Intelligence**, sekalian buat nerapin materi-materi kuliah ke data *real-world*. Di sini, aku ngambil studi kasus dari Erigo Store (salah satu brand fashion lokal yang cukup gede) buat ngelihat gimana sih strategi harga, diskon, dan kondisi stok mereka.

Semua proses dari awal narik data (scraping) sampai datanya siap dibikin visualisasi (Tableau) aku kerjain end-to-end di project ini.

## 🚀 Apa Aja yang Dikerjain?

Project ini dibagi jadi beberapa tahap biar rapi:

1. **Tahap 1: Data Scraping (`scraper.py`)** 
   Aku bikin script Python sederhana buat narik data langsung dari endpoint JSON-nya Shopify. Sengaja pakai cara ini biar lebih cepet dan nggak ngebebanin server mereka dibanding pakai Selenium. Scriptnya udah aku tambahin *retry logic* sama *delay* biar aman.
2. **Tahap 2: Data Cleaning & Engineering (`02_data_engineering.py`)**
   Nah, data mentah dari scraping kan masih berantakan. Di script ini aku beresin data yang bolong (misal: kategori kosong aku tebak dari nama produknya), ngecek harga diskon yang aneh, sampai nambahin fitur baru kayak ngitung *persentase diskon* atau nge-flag produk kolaborasi (kayak JKT48, MPL, dll).
3. **Tahap 3: Database Storage (`erigo_store.db`)**
   Biar gampang di-query atau ditarik ke tools BI, data yang udah bersih aku simpen ke database SQLite lokal.
4. **Tahap 4 & 5: Visualisasi (Tableau) & Data Science**
   *(Bagian ini masih *on progress*! Rencananya aku mau bikin dashboard di Tableau dan sedikit clustering buat segmentasi harga)*.

## 📂 Isi Repository

```text
├── scraper.py                 # Script buat narik data JSON dari Shopify
├── 02_data_engineering.py     # Script ETL buat ngebersihin & nambah fitur
├── requirements.txt           # List library Python yang aku pakai
├── .gitignore                 # Biar file raw yg gede/cache ga ikut ke-push
├── erigo_store.db             # Database SQLite isi data bersih
└── erigo_*_clean.csv          # File CSV yang udah siap di-import ke Tableau
```

## 📊 Insight Singkat Sejauh Ini

Dari data terakhir yang berhasil aku kumpulin (**309 produk unik dan 1.623 varian**), ada beberapa *finding* lumayan menarik:
- **Diskonnya jor-joran:** Ternyata 95.5% dari katalog produk mereka lagi diskon!
- **Rata-rata potongannya gede:** Secara rata-rata, mereka ngasih diskon sekitar **43.2%**.
- **Fokus di harga tengah:** Hampir 58% produk mereka ada di rentang harga Rp100rb - Rp200rb (Mid-segment).
- **Kolaborasi = Beda strategi:** Produk-produk kolaborasi kayak edisi JKT48 atau M6 kelihatan punya perlakuan harga dan stok yang agak beda.

## 🛠️ Cara Nyobain Kode Ini

Kalau kamu mau coba *run* sendiri di komputer kamu:

1. Clone repo ini dulu:
   ```bash
   git clone https://github.com/JonathanMangiring/erigo-data-pipeline.git
   cd erigo-data-pipeline
   ```
2. Install library yang dibutuhin:
   ```bash
   pip install -r requirements.txt
   ```
3. Run script-nya berurutan:
   ```bash
   # 1. Scraping data terbaru
   python scraper.py

   # 2. Cleaning dan masukin ke database
   python 02_data_engineering.py
   ```

---
*Project ini murni dibuat untuk tujuan edukasi dan portofolio.* Kalau ada masukan atau mau diskusi soal data, *feel free* buat *connect* ya! 

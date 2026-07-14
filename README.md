# 🛍️ E-Commerce Data Pipeline & Analytics (Erigo Store)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Manipulation-150458.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)
![Tableau](https://img.shields.io/badge/Tableau-Business_Intelligence-E97627.svg)
![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen.svg)

An **end-to-end Data Engineering and Business Intelligence portfolio project** analyzing e-commerce product data from Erigo Store (a major Indonesian fashion retailer). This project demonstrates the complete data lifecycle: from raw data extraction (Scraping) to structured storage (SQLite), and actionable business insights (Tableau).

## 🚀 Project Overview

The goal of this project is to build a robust pipeline that automates the collection, cleaning, and analysis of e-commerce catalog data to answer key business questions such as pricing strategies, discount depths, stock-out risks, and product categorizations.

### 🏗️ Pipeline Architecture

1. **Data Collection (Scraping):** Custom Python scraper interacting with Shopify's public `/products.json` endpoint with retry logic, exponential backoff, and pagination.
2. **Data Engineering (ETL):** Cleaning anomalies, handling missing values (inferring categories from titles), and feature enrichment (calculating discount percentages, detecting collaborations like JKT48/MPL).
3. **Data Storage:** Structuring the flattened data into a relational database (`SQLite`) with normalized tables.
4. **Business Intelligence:** Interactive Tableau dashboards to visualize catalog health, pricing segments, and stock risks. *(In Progress)*
5. **Data Science:** Price clustering and text analysis on product naming conventions. *(Upcoming)*

## 📂 Repository Structure

```text
├── scraper.py                 # Tahap 1: Python scraper (Shopify JSON endpoint)
├── 02_data_engineering.py     # Tahap 2: Data cleaning, enrichment & SQLite export
├── requirements.txt           # Python dependencies
├── .gitignore                 # Excludes raw heavy files and caches
├── erigo_store.db             # Output: SQLite Database (Cleaned Data)
└── erigo_*_clean.csv          # Output: Cleaned CSVs ready for Tableau
```

## 📊 Key Findings (Initial Data)

From the recent extraction of **309 unique products and 1,623 variants**:
- **Aggressive Discounting:** 95.5% of the catalog is currently on sale.
- **Average Discount Depth:** The average price cut across discounted items is **43.2%**.
- **Price Segmentation:** The brand heavily dominates the "Mid" tier (Rp100k - Rp200k), making up ~58% of the catalog.
- **Collaborations:** Successfully detected and isolated special collaboration items (e.g., JKT48, M6, MPL) which exhibit different pricing behaviors.

## 🛠️ How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the pipeline:
   ```bash
   # Step 1: Collect raw data
   python scraper.py

   # Step 2: Clean and load to Database
   python 02_data_engineering.py
   ```

## 👨‍💻 Author
Built as a Data Engineering & Analytics portfolio piece. Connect with me to discuss data!

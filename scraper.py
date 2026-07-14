"""
Scraper untuk toko Shopify Erigo (erigostore.co.id)
=====================================================
Memanfaatkan endpoint publik Shopify /products.json — TIDAK perlu Selenium/Playwright
karena Shopify mengekspos data produk dalam format JSON terstruktur secara default.

Endpoint ini publik dan legal diakses (dipakai juga oleh Google Shopping feed, dsb),
namun tetap gunakan rate-limiting yang sopan agar tidak membebani server toko.

Requirement:
    pip install requests pandas --break-system-packages

Output:
    - erigo_products_raw.json   -> data mentah semua produk (untuk arsip/debug)
    - erigo_products_flat.csv   -> 1 baris = 1 produk (agregat harga min/max)
    - erigo_variants_flat.csv   -> 1 baris = 1 varian (size/warna), untuk analisis granular
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime

# ------------------------------------------------------------------
# KONFIGURASI
# ------------------------------------------------------------------
BASE_URL = "https://erigostore.co.id"
PRODUCTS_ENDPOINT = f"{BASE_URL}/products.json"
LIMIT_PER_PAGE = 250          # maksimum yang diizinkan Shopify per request
DELAY_BETWEEN_REQUESTS = 2.0  # detik, sopan terhadap server
MAX_RETRIES = 4                # max retry per halaman jika timeout
RETRY_DELAY = 5.0              # detik jeda antar retry
REQUEST_TIMEOUT = 30           # timeout per request (detik) — lebih longgar dari sebelumnya
HEADERS = {
    # User-Agent wajar, bukan untuk menyamar sebagai browser tertentu secara agresif
    "User-Agent": "Mozilla/5.0 (compatible; PortfolioResearchBot/1.0; +educational-purpose)",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


def fetch_page_with_retry(page: int, session: requests.Session) -> list:
    """
    Ambil satu halaman produk dengan retry logic.
    Mengembalikan list produk, atau [] jika gagal semua retry.
    """
    params = {"limit": LIMIT_PER_PAGE, "page": page}
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  [INFO] Halaman {page} — percobaan {attempt}/{MAX_RETRIES} ...")
            resp = session.get(
                PRODUCTS_ENDPOINT,
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            products = resp.json().get("products", [])
            print(f"  [OK]   Halaman {page}: {len(products)} produk berhasil diambil.")
            return products

        except requests.exceptions.Timeout:
            print(f"  [WARN] Timeout pada halaman {page} (percobaan {attempt}). "
                  f"Tunggu {RETRY_DELAY}s lalu retry...")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"  [ERROR] Halaman {page} gagal setelah {MAX_RETRIES} percobaan. Lanjut ke halaman berikutnya.")
                return []

        except requests.exceptions.ConnectionError as e:
            print(f"  [WARN] Connection error halaman {page} (percobaan {attempt}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)  # exponential backoff
            else:
                print(f"  [ERROR] Halaman {page} — koneksi gagal total.")
                return []

        except requests.RequestException as e:
            print(f"  [ERROR] Gagal halaman {page}: {e}")
            return []

    return []


def fetch_all_products() -> list:
    """
    Ambil seluruh produk dari toko dengan pagination sampai halaman kosong.
    Menggunakan session untuk reuse koneksi TCP.
    """
    all_products = []
    consecutive_empty = 0  # stop jika 2 halaman berturut-turut kosong
    
    # Gunakan session untuk efisiensi koneksi
    with requests.Session() as session:
        for page in range(1, 100):  # max 100 halaman (25.000 produk) — safety limit
            print(f"\n[PAGE {page}]")
            products = fetch_page_with_retry(page, session)

            if not products:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    print(f"[INFO] 2 halaman berturut-turut kosong/gagal. Scraping selesai.")
                    break
                else:
                    print(f"[WARN] Halaman {page} kosong/gagal. Coba halaman berikutnya...")
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                    continue
            else:
                consecutive_empty = 0

            all_products.extend(products)
            print(f"[TOTAL] {len(all_products)} produk terkumpul sejauh ini.")

            # Jika halaman ini tidak penuh, berarti sudah halaman terakhir
            if len(products) < LIMIT_PER_PAGE:
                print(f"[INFO] Halaman {page} tidak penuh ({len(products)} < {LIMIT_PER_PAGE}). "
                      f"Ini halaman terakhir.")
                break

            time.sleep(DELAY_BETWEEN_REQUESTS)

    return all_products


def flatten_products(products: list) -> tuple:
    """
    Ubah data JSON mentah menjadi dua tabel:
    1. products_flat  -> level produk (agregat dari semua variannya)
    2. variants_flat  -> level varian (granular: tiap ukuran/warna)
    """
    products_rows = []
    variants_rows = []

    for p in products:
        variants = p.get("variants", [])
        prices = [float(v["price"]) for v in variants if v.get("price")]
        compare_prices = [float(v["compare_at_price"]) for v in variants if v.get("compare_at_price")]

        available_count = sum(1 for v in variants if v.get("available"))
        total_variants = len(variants)

        product_row = {
            "product_id": p.get("id"),
            "title": p.get("title"),
            "handle": p.get("handle"),
            "product_url": f"{BASE_URL}/products/{p.get('handle')}",
            "product_type": p.get("product_type"),
            "vendor": p.get("vendor"),
            "tags": ", ".join(p.get("tags", [])),
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
            "published_at": p.get("published_at"),
            "price_min": min(prices) if prices else None,
            "price_max": max(prices) if prices else None,
            "compare_at_price_max": max(compare_prices) if compare_prices else None,
            "is_on_sale": any(
                v.get("compare_at_price") and float(v["compare_at_price"]) > float(v["price"])
                for v in variants if v.get("price")
            ),
            "total_variants": total_variants,
            "available_variants": available_count,
            "stock_status": "in_stock" if available_count > 0 else "sold_out",
            "image_count": len(p.get("images", [])),
            "main_image_url": p.get("images", [{}])[0].get("src") if p.get("images") else None,
        }
        products_rows.append(product_row)

        # level varian (granular)
        for v in variants:
            variants_rows.append({
                "product_id": p.get("id"),
                "product_title": p.get("title"),
                "variant_id": v.get("id"),
                "variant_title": v.get("title"),
                "sku": v.get("sku"),
                "price": v.get("price"),
                "compare_at_price": v.get("compare_at_price"),
                "available": v.get("available"),
                "option1": v.get("option1"),  # biasanya size
                "option2": v.get("option2"),  # biasanya warna
                "option3": v.get("option3"),
            })

    return pd.DataFrame(products_rows), pd.DataFrame(variants_rows)


def main():
    print("=" * 60)
    print("SCRAPING ERIGO STORE (Shopify /products.json)")
    print(f"Timeout: {REQUEST_TIMEOUT}s | Max Retries: {MAX_RETRIES} | Delay: {DELAY_BETWEEN_REQUESTS}s")
    print("=" * 60)

    start_time = datetime.now()
    products = fetch_all_products()
    elapsed = (datetime.now() - start_time).seconds

    print(f"\n[SELESAI] Total produk terkumpul: {len(products)} (dalam {elapsed} detik)\n")

    if not products:
        print("[WARNING] Tidak ada produk yang berhasil diambil. Cek koneksi/endpoint.")
        return

    # Simpan data mentah (arsip lengkap, jaga-jaga field yang belum dipakai)
    raw_filename = "erigo_products_raw.json"
    with open(raw_filename, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"[SAVED] Data mentah -> {raw_filename}")

    # Flatten ke tabel siap analisis
    df_products, df_variants = flatten_products(products)

    products_csv = "erigo_products_flat.csv"
    variants_csv = "erigo_variants_flat.csv"
    df_products.to_csv(products_csv, index=False)
    df_variants.to_csv(variants_csv, index=False)

    print(f"[SAVED] Tabel produk ({len(df_products)} baris) -> {products_csv}")
    print(f"[SAVED] Tabel varian ({len(df_variants)} baris) -> {variants_csv}")

    # Ringkasan cepat
    print("\n" + "=" * 60)
    print("RINGKASAN CEPAT")
    print("=" * 60)
    print(f"Total produk unik      : {len(df_products)}")
    print(f"Total varian (SKU)     : {len(df_variants)}")
    print(f"Produk sedang diskon   : {df_products['is_on_sale'].sum()} ({df_products['is_on_sale'].mean()*100:.1f}%)")
    print(f"Produk sold out        : {(df_products['stock_status']=='sold_out').sum()}")
    print(f"Kategori (product_type): {df_products['product_type'].nunique()} kategori unik")
    print(f"\nDistribusi kategori (top 10):")
    print(df_products['product_type'].value_counts().head(10))
    print(f"\nRentang harga:")
    print(f"  Min: Rp{df_products['price_min'].min():,.0f}")
    print(f"  Max: Rp{df_products['price_min'].max():,.0f}")
    print(f"  Rata-rata: Rp{df_products['price_min'].mean():,.0f}")
    print(f"\nDiambil pada: {datetime.now().isoformat()}")
    print(f"Durasi scraping: {elapsed} detik")


if __name__ == "__main__":
    main()
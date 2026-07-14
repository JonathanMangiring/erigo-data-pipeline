"""
Tahap 2 — Data Engineering: Cleaning, Enrichment & SQLite Storage
==================================================================
Input  : erigo_products_flat.csv, erigo_variants_flat.csv
Output : erigo_store.db (SQLite) + erigo_products_clean.csv, erigo_variants_clean.csv

Yang dilakukan:
  1. Cleaning   — isi product_type kosong, normalisasi size, flag duplikat, parse tanggal
  2. Enrichment — tambah kolom turunan: discount_pct, is_collab, price_segment, dll.
  3. Storage    — simpan ke SQLite (3 tabel: products, variants, category_lookup)

Requirement: pip install pandas
"""

import pandas as pd
import sqlite3
import re
import json
from datetime import datetime, timezone

# ──────────────────────────────────────────────
# 0. LOAD DATA
# ──────────────────────────────────────────────
print("=" * 60)
print("TAHAP 2 — DATA ENGINEERING")
print("=" * 60)

df_prod = pd.read_csv("erigo_products_flat.csv")
df_var  = pd.read_csv("erigo_variants_flat.csv")

print(f"\n[LOAD] Products  : {len(df_prod)} baris, {df_prod.shape[1]} kolom")
print(f"[LOAD] Variants  : {len(df_var)} baris, {df_var.shape[1]} kolom")

# ──────────────────────────────────────────────
# 1. CLEANING — PRODUCTS
# ──────────────────────────────────────────────
print("\n[STEP 1] Cleaning products ...")

# 1a. Parse tanggal
date_cols = ["created_at", "updated_at", "published_at"]
for col in date_cols:
    df_prod[col] = pd.to_datetime(df_prod[col], utc=True, errors="coerce")

# 1b. Inferensi product_type kosong dari title
TITLE_TYPE_MAP = {
    r"\bT-Shirt\b|\bKaos\b": "T-Shirt",
    r"\bJogger\b": "Jogger Pants",
    r"\bChino Pants\b": "Chino Pants",
    r"\bHoodie\b": "Hoodie",
    r"\bSweater\b|\bSweatshirt\b": "Sweatshirt",
    r"\bJacket\b|\bJaket\b": "Jacket",
    r"\bShirt\b|\bKemeja\b": "Shirt",
    r"\bKoko\b|\bShanghai\b": "Koko",
    r"\bPants\b|\bCelana\b": "Pants",
    r"\bCargo\b": "Cargo Pants",
    r"\bDenim\b": "Denim",
    r"\bFlannel\b": "Flannel Shirt",
    r"\bBomber\b": "Bomber",
    r"\bVarsity\b": "Varsity",
    r"\bJersey\b": "Jersey",
    r"\bSandal\b": "Sandal",
    r"\bCaps\b|\bSnapback\b": "Caps",
    r"\bTote\b|\bDaypack\b|\bBag\b": "Bag",
    r"\bPullover\b": "Pullover",
    r"\bActi(ve|vity)\b": "Active Wear",
    r"\bSet\b": "Bundle Set",
}

empty_type_mask = df_prod["product_type"].isna() | (df_prod["product_type"] == "")
n_empty = empty_type_mask.sum()

def infer_type(title: str) -> str:
    if not isinstance(title, str):
        return "Other"
    for pattern, category in TITLE_TYPE_MAP.items():
        if re.search(pattern, title, re.IGNORECASE):
            return category
    return "Other"

df_prod.loc[empty_type_mask, "product_type"] = df_prod.loc[empty_type_mask, "title"].apply(infer_type)
print(f"  → {n_empty} produk product_type kosong → diisi dari title")

# 1c. Flag duplikat (title mengandung "(Copy)")
df_prod["is_duplicate"] = df_prod["title"].str.contains(r"\(Copy\)", case=False, na=False)
n_dup = df_prod["is_duplicate"].sum()
print(f"  → {n_dup} produk terdeteksi duplikat (mengandung '(Copy)')")

# 1d. Fix is_on_sale anomali (compare_at_price < price → bukan diskon)
anomaly_mask = (
    df_prod["compare_at_price_max"].notna() &
    (df_prod["compare_at_price_max"] <= df_prod["price_min"])
)
df_prod.loc[anomaly_mask, "is_on_sale"] = False
print(f"  → {anomaly_mask.sum()} produk compare_at_price anomali dikoreksi")

# ──────────────────────────────────────────────
# 2. ENRICHMENT — PRODUCTS
# ──────────────────────────────────────────────
print("\n[STEP 2] Enrichment products ...")

now_utc = pd.Timestamp.now(tz="UTC")

# 2a. Discount percentage
df_prod["discount_pct"] = (
    (df_prod["compare_at_price_max"] - df_prod["price_min"]) /
    df_prod["compare_at_price_max"] * 100
).round(1)
df_prod.loc[~df_prod["is_on_sale"], "discount_pct"] = 0.0

# 2b. Days since launch
df_prod["days_since_launch"] = (now_utc - df_prod["created_at"]).dt.days

# 2c. Produk baru (< 30 hari)
df_prod["is_new_product"] = df_prod["days_since_launch"] <= 30

# 2d. Kolaborasi detection
COLLAB_PATTERNS = {
    "JKT48": r"JKT.?48|Final Dance",
    "M6":    r"\bM6\b|Sacred",
    "MPL":   r"\bMPL\b",
    "EVOS":  r"\bEVOS\b",
    "ONIC":  r"\bONIC\b",
    "MLBB":  r"Mobile.?Legend|\bMLBB\b",
}

def detect_collab(text: str) -> tuple:
    if not isinstance(text, str):
        return (False, None)
    for partner, pattern in COLLAB_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return (True, partner)
    return (False, None)

collab_results = (df_prod["title"] + " " + df_prod["tags"].fillna("")).apply(detect_collab)
df_prod["is_collab_product"] = collab_results.apply(lambda x: x[0])
df_prod["collab_partner"]    = collab_results.apply(lambda x: x[1])

n_collab = df_prod["is_collab_product"].sum()
print(f"  → {n_collab} produk kolaborasi terdeteksi:")
if n_collab > 0:
    print(df_prod[df_prod["is_collab_product"]][["title","collab_partner"]].to_string(index=False))

# 2e. Price segment
def price_segment(price):
    if pd.isna(price):     return "unknown"
    if price < 100_000:    return "budget"
    if price < 200_000:    return "mid"
    if price < 300_000:    return "premium"
    return "luxury"

df_prod["price_segment"] = df_prod["price_min"].apply(price_segment)

# 2f. Stock ratio (persen varian yang tersedia)
df_prod["stock_ratio"] = (df_prod["available_variants"] / df_prod["total_variants"]).round(3)
df_prod["stock_ratio"] = df_prod["stock_ratio"].fillna(0.0)

# 2g. Stock risk label
def stock_risk(row):
    if row["stock_status"] == "sold_out":   return "critical"
    if row["stock_ratio"] <= 0.2:            return "high"
    if row["stock_ratio"] <= 0.5:            return "medium"
    return "low"

df_prod["stock_risk"] = df_prod.apply(stock_risk, axis=1)

# 2h. Category group (dari product_type → grup besar untuk Tableau)
CATEGORY_GROUP = {
    "tops": [
        "T-Shirt", "T-Shirt Graphic", "T-Shirt Japan Series", "T-Shirt Embro",
        "T-Shirt Oversize Hd", "T-Shirt Oversize Pocket", "T-Shirt Contrast Stitch",
        "T-Shirt Adventure", "T-Shirt Long Sleeve Oversize", "T-Shirt Oversize Pocket Furlan",
        "Erigo X JKT48 Final Dance", "Erigo X M6 T-Shirt", "Active Tees",
        "Raglan Short Sleeve Movease", "Long Sleeve Hoodie Tees", "Jersey", "Short Sleeve Pocket",
    ],
    "bottoms": [
        "Chino Pants", "Chino Pants Super Stretch", "Jogger Pants", "Jogger Pants Super Stretch",
        "Jogger Zipper", "Denim Pants", "Denim Pants Washing", "Relax Chino Pants",
        "Cargo Pants Twill", "Cargo Pants UT", "Five Pocket Pants", "Chino Short Super Stretch",
    ],
    "outerwear": [
        "Hoodie", "Hoodie Typography", "Hoodie Embro", "Sweatshirt", "Sweatshirt Hd Typography",
        "Pullover", "Bomber", "Flight Jacket", "Denim Jacket Pocket", "Coach Jacket Graphic",
        "Varsity Classic", "Shacket (Shirt Jacket)", "Ultra Lightweight Jacket",
    ],
    "shirts": [
        "Flannel Shirt", "Short Shirt", "Short Shirt Pocket", "Short Sleeve Pocket",
        "Basic Long Sleeve Shirt Oxford", "Koko Short Sleeve Bordir", "Koko Long Sleeve Bordir",
        "Koko Short Sleeve Basic", "Koko Long Sleeve Basic", "Shanghai Short Sleeve 2025",
        "Shanghai Long Sleeve 2025",
    ],
    "accessories": [
        "Sandal", "Snapback", "Five Panel Caps", "Totebag Street/College", "Daypack College",
    ],
    "sets": [
        "Bundle Set",
    ],
}

type_to_group = {}
for group, types in CATEGORY_GROUP.items():
    for t in types:
        type_to_group[t] = group

def get_category_group(product_type):
    if not isinstance(product_type, str):
        return "other"
    # cek exact match dulu
    if product_type in type_to_group:
        return type_to_group[product_type]
    # fallback: keyword match
    pt_lower = product_type.lower()
    if any(k in pt_lower for k in ["shirt", "tee", "kaos", "jersey", "raglan"]): return "tops"
    if any(k in pt_lower for k in ["pants", "jogger", "chino", "denim", "cargo", "celana"]): return "bottoms"
    if any(k in pt_lower for k in ["hoodie", "jacket", "sweat", "bomber", "varsity", "pullover"]): return "outerwear"
    if any(k in pt_lower for k in ["koko", "flannel", "shanghai"]): return "shirts"
    if any(k in pt_lower for k in ["cap", "sandal", "bag", "daypack"]): return "accessories"
    return "other"

df_prod["category_group"] = df_prod["product_type"].apply(get_category_group)

print(f"\n  Distribusi category_group:")
print(df_prod["category_group"].value_counts().to_string())

# 2i. Design theme detection dari title
DESIGN_THEMES = {
    "military":   r"military|army|cargo|tactical",
    "oversize":   r"oversize|os\b",
    "japanese":   r"japan|japanese|tokyo|kyoto|osaka|Y[ao]|Yuki|Yoshi|Yahiko",
    "islamic":    r"koko|shanghai|bordir|ramadhan",
    "graphic":    r"graphic|print|tee",
    "collab":     r"JKT|MPL|EVOS|ONIC|M6|Final Dance",
    "outdoor":    r"adventure|hiking|surfing|mountain",
    "streetwear": r"varsity|bomber|denim|flannel|coach",
}

for theme, pattern in DESIGN_THEMES.items():
    df_prod[f"theme_{theme}"] = df_prod["title"].str.contains(pattern, case=False, na=False)

# ──────────────────────────────────────────────
# 3. CLEANING — VARIANTS
# ──────────────────────────────────────────────
print("\n[STEP 3] Cleaning variants ...")

# 3a. Normalisasi option1 (size): "S (45-50kg)*" → "S"
def normalize_size(s):
    if not isinstance(s, str):
        return s
    # Ambil bagian sebelum spasi atau tanda kurung
    clean = re.match(r"^([A-Z0-9]+)", s.strip())
    return clean.group(1) if clean else s

df_var["size_clean"] = df_var["option1"].apply(normalize_size)

# 3b. Konversi harga ke numerik
df_var["price"]           = pd.to_numeric(df_var["price"], errors="coerce")
df_var["compare_at_price"] = pd.to_numeric(df_var["compare_at_price"], errors="coerce")

# 3c. Kolom discount per varian
df_var["variant_discount_pct"] = (
    (df_var["compare_at_price"] - df_var["price"]) /
    df_var["compare_at_price"] * 100
).round(1)
df_var["variant_discount_pct"] = df_var["variant_discount_pct"].clip(lower=0).fillna(0)

print(f"  → Size normalization selesai. Unique sizes: {df_var['size_clean'].nunique()}")
print(f"    Sizes: {sorted(df_var['size_clean'].dropna().unique().tolist())[:20]}")

# ──────────────────────────────────────────────
# 4. SAVE CLEAN CSV (untuk Tableau)
# ──────────────────────────────────────────────
print("\n[STEP 4] Menyimpan CSV bersih untuk Tableau ...")

# Convert datetime ke string untuk CSV agar Tableau baca dengan benar
df_prod_save = df_prod.copy()
for col in date_cols:
    df_prod_save[col] = df_prod_save[col].dt.strftime("%Y-%m-%d")

df_prod_save.to_csv("erigo_products_clean.csv", index=False, encoding="utf-8-sig")
df_var.to_csv("erigo_variants_clean.csv", index=False, encoding="utf-8-sig")
print(f"  → erigo_products_clean.csv ({len(df_prod_save)} baris)")
print(f"  → erigo_variants_clean.csv ({len(df_var)} baris)")

# ──────────────────────────────────────────────
# 5. SAVE TO SQLITE
# ──────────────────────────────────────────────
print("\n[STEP 5] Menyimpan ke SQLite (erigo_store.db) ...")

conn = sqlite3.connect("erigo_store.db")

# Konversi datetime ke string untuk SQLite
df_prod_db = df_prod.copy()
for col in date_cols:
    df_prod_db[col] = df_prod_db[col].astype(str)

# Simpan tabel utama
df_prod_db.to_sql("products", conn, if_exists="replace", index=False)
df_var.to_sql("variants", conn, if_exists="replace", index=False)

# Tabel lookup kategori
cat_lookup = pd.DataFrame([
    {"product_type": ptype, "category_group": group}
    for group, types in CATEGORY_GROUP.items()
    for ptype in types
])
cat_lookup.to_sql("category_lookup", conn, if_exists="replace", index=False)

# Tabel kolaborasi
collab_summary = df_prod[df_prod["is_collab_product"]].groupby("collab_partner").agg(
    product_count=("product_id", "count"),
    avg_price=("price_min", "mean"),
    avg_discount=("discount_pct", "mean"),
).reset_index()
collab_summary.to_sql("collab_summary", conn, if_exists="replace", index=False)

# Verifikasi quick
cursor = conn.cursor()
for tbl in ["products", "variants", "category_lookup", "collab_summary"]:
    count = cursor.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"  → Tabel '{tbl}': {count} baris")

conn.close()

# ──────────────────────────────────────────────
# 6. RINGKASAN DATA ENGINEERING
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("RINGKASAN DATA ENGINEERING")
print("=" * 60)

print(f"\nPRODUCTS ({len(df_prod)} baris):")
print(f"  Kolom baru ditambahkan  : discount_pct, days_since_launch, is_new_product,")
print(f"                            is_collab_product, collab_partner, price_segment,")
print(f"                            stock_ratio, stock_risk, category_group,")
print(f"                            theme_military, theme_oversize, theme_japanese, ...")
print(f"\n  Price segments:")
print(df_prod["price_segment"].value_counts().to_string())
print(f"\n  Stock risk distribution:")
print(df_prod["stock_risk"].value_counts().to_string())
print(f"\n  Kolaborasi terdeteksi:")
if collab_summary is not None and len(collab_summary) > 0:
    print(collab_summary.to_string(index=False))
else:
    print("  (Tidak ada kolaborasi terdeteksi)")
print(f"\n  Produk baru (<30 hari): {df_prod['is_new_product'].sum()}")
print(f"  Rata-rata discount    : {df_prod.loc[df_prod['is_on_sale'], 'discount_pct'].mean():.1f}%")
print(f"  Rata-rata days_since_launch: {df_prod['days_since_launch'].mean():.0f} hari")

print(f"\nVARIANTS ({len(df_var)} baris):")
print(f"  Kolom baru: size_clean, variant_discount_pct")
print(f"  Unique sizes: {df_var['size_clean'].nunique()}")

print(f"\nOUTPUT FILES:")
print(f"  erigo_products_clean.csv  → untuk Tableau")
print(f"  erigo_variants_clean.csv  → untuk Tableau")
print(f"  erigo_store.db            → untuk SQL query / analisis DS")

print(f"\nSelesai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

"""
01_load_to_sql.py
-----------------
Loads the raw Superstore CSV into a SQLite database (retail.db).

What this script does:
- Reads the flat CSV (one row per order line)
- Splits it into 3 normalised tables:
    regions   : region + state + city lookup
    products  : product category, sub-category
    orders    : the main fact table (sales, profit, qty, discount)
- Writes all 3 tables to data/retail.db
- Verifies row counts after loading

Why normalise?
  The raw CSV has repeated strings like "Office Supplies" and "West"
  on every row. Splitting into lookup tables is standard DB design —
  it's also what interviewers expect you to know.
"""

import pandas as pd
import sqlite3
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE   = os.path.join(BASE_DIR, "data", "SampleSuperstore.csv")
DB_PATH    = os.path.join(BASE_DIR, "data", "retail.db")

# ── Load raw data ─────────────────────────────────────────────────────────────
print("Loading raw CSV...")
df = pd.read_csv(RAW_FILE, encoding="latin1")
print(f"  {len(df):,} rows, {len(df.columns)} columns loaded.\n")

# Normalise column names
df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

# Add a surrogate row ID (acts as order_line_id)
df = df.reset_index().rename(columns={"index": "order_line_id"})
df["order_line_id"] += 1   # 1-indexed

# ── Build lookup tables ───────────────────────────────────────────────────────

# 1. regions table  (region / state / city combinations)
regions = (
    df[["region", "state", "city"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
regions.insert(0, "region_id", range(1, len(regions) + 1))
print(f"regions table    : {len(regions):,} rows")

# 2. products table  (category / sub-category combinations)
products = (
    df[["category", "sub_category"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
products.insert(0, "product_id", range(1, len(products) + 1))
print(f"products table   : {len(products):,} rows")

# 3. orders (fact table) — merge FKs back in, keep raw metrics
orders = df.merge(
    regions,  on=["region", "state", "city"],        how="left"
).merge(
    products, on=["category", "sub_category"],        how="left"
)[
    [
        "order_line_id",
        "region_id",
        "product_id",
        "segment",
        "ship_mode",
        "sales",
        "quantity",
        "discount",
        "profit",
    ]
]
print(f"orders table     : {len(orders):,} rows\n")

# ── Write to SQLite ───────────────────────────────────────────────────────────
print(f"Writing to {DB_PATH} ...")

# Remove existing DB so we always start clean
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)

regions.to_sql("regions",  conn, index=False, if_exists="replace")
products.to_sql("products", conn, index=False, if_exists="replace")
orders.to_sql("orders",   conn, index=False, if_exists="replace")

# ── Add indexes for faster JOINs ──────────────────────────────────────────────
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_region  ON orders(region_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id)")
conn.commit()

# ── Verify ────────────────────────────────────────────────────────────────────
print("\nVerification — row counts in DB:")
for table in ["regions", "products", "orders"]:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<12}: {count:,} rows")

conn.close()
print("\nDone. retail.db is ready.")

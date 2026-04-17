"""
02_query_kpis.py
----------------
Runs 5 SQL queries against retail.db and saves each result
as a CSV to data/ for use by the analysis and forecast scripts.

KPIs calculated entirely in SQL:
  - Revenue & profit margin by region
  - Revenue & margin by product category
  - Revenue & margin by sub-category (top 10)
  - Revenue by customer segment
  - Monthly revenue trend (using order_line_id as a time proxy)

SQL concepts used:
  JOIN          : links orders → regions and orders → products
  GROUP BY      : aggregates metrics per dimension
  ROUND()       : rounds to 2 decimal places inside SQL
  CAST / 1.0    : forces float division (SQLite is integer by default)
  ORDER BY DESC : sorts results for readability
"""

import sqlite3
import pandas as pd
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, "data", "retail.db")
DATA_DIR  = os.path.join(BASE_DIR, "data")

conn = sqlite3.connect(DB_PATH)
print(f"Connected to {DB_PATH}\n")

# ── Helper ────────────────────────────────────────────────────────────────────
def run(label, sql, save_as):
    """Run a query, print it, save result to CSV."""
    print(f"{'='*55}")
    print(f"QUERY: {label}")
    print(f"{'='*55}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    out = os.path.join(DATA_DIR, save_as)
    df.to_csv(out, index=False)
    print(f"\n  Saved → {save_as}\n")
    return df

# ── Query 1: Revenue & margin by REGION ───────────────────────────────────────
run(
    label   = "Revenue & profit margin by region",
    save_as = "kpi_by_region.csv",
    sql     = """
    SELECT
        r.region,
        ROUND(SUM(o.sales), 2)                                  AS total_revenue,
        ROUND(SUM(o.profit), 2)                                 AS total_profit,
        ROUND(SUM(o.profit) / SUM(o.sales) * 100.0, 2)         AS margin_pct,
        COUNT(o.order_line_id)                                  AS order_lines
    FROM orders o
    JOIN regions r ON o.region_id = r.region_id
    GROUP BY r.region
    ORDER BY total_revenue DESC
    """
)

# ── Query 2: Revenue & margin by CATEGORY ─────────────────────────────────────
run(
    label   = "Revenue & profit margin by category",
    save_as = "kpi_by_category.csv",
    sql     = """
    SELECT
        p.category,
        ROUND(SUM(o.sales), 2)                                  AS total_revenue,
        ROUND(SUM(o.profit), 2)                                 AS total_profit,
        ROUND(SUM(o.profit) / SUM(o.sales) * 100.0, 2)         AS margin_pct,
        COUNT(o.order_line_id)                                  AS order_lines
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC
    """
)

# ── Query 3: Top 10 sub-categories by revenue ────────────────────────────────
run(
    label   = "Top 10 sub-categories by revenue",
    save_as = "kpi_by_subcategory.csv",
    sql     = """
    SELECT
        p.sub_category,
        p.category,
        ROUND(SUM(o.sales), 2)                                  AS total_revenue,
        ROUND(SUM(o.profit), 2)                                 AS total_profit,
        ROUND(SUM(o.profit) / SUM(o.sales) * 100.0, 2)         AS margin_pct
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.sub_category
    ORDER BY total_revenue DESC
    LIMIT 10
    """
)

# ── Query 4: Revenue by customer SEGMENT ──────────────────────────────────────
run(
    label   = "Revenue & margin by customer segment",
    save_as = "kpi_by_segment.csv",
    sql     = """
    SELECT
        o.segment,
        ROUND(SUM(o.sales), 2)                                  AS total_revenue,
        ROUND(SUM(o.profit), 2)                                 AS total_profit,
        ROUND(SUM(o.profit) / SUM(o.sales) * 100.0, 2)         AS margin_pct,
        COUNT(o.order_line_id)                                  AS order_lines
    FROM orders o
    GROUP BY o.segment
    ORDER BY total_revenue DESC
    """
)

# ── Query 5: Discount impact on profit margin ────────────────────────────────
# Buckets: no discount / low (≤20%) / medium (≤40%) / high (>40%)
run(
    label   = "Profit margin by discount band",
    save_as = "kpi_by_discount.csv",
    sql     = """
    SELECT
        CASE
            WHEN o.discount = 0              THEN '0 — No discount'
            WHEN o.discount <= 0.20          THEN '1 — Low  (≤20%)'
            WHEN o.discount <= 0.40          THEN '2 — Mid  (≤40%)'
            ELSE                                  '3 — High (>40%)'
        END                                                     AS discount_band,
        COUNT(o.order_line_id)                                  AS order_lines,
        ROUND(SUM(o.sales), 2)                                  AS total_revenue,
        ROUND(SUM(o.profit), 2)                                 AS total_profit,
        ROUND(SUM(o.profit) / SUM(o.sales) * 100.0, 2)         AS margin_pct
    FROM orders o
    GROUP BY discount_band
    ORDER BY discount_band
    """
)

conn.close()
print("All 5 KPI tables saved to data/\n")

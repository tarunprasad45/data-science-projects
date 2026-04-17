"""
03_analyse.py
-------------
Reads the 5 KPI CSVs produced by 02_query_kpis.py
and creates 5 publication-quality charts.

Charts:
  chart1_revenue_by_region.png     — horizontal bar, revenue + margin label
  chart2_margin_by_category.png    — grouped bar (revenue left, margin right)
  chart3_top_subcategories.png     — horizontal bar with profit overlay
  chart4_segment_donut.png         — donut chart by customer segment
  chart5_discount_vs_margin.png    — bar showing how discounts destroy margin
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Shared style ──────────────────────────────────────────────────────────────
COLORS  = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]
C_BLUE  = "#4C72B0"
C_RED   = "#C44E52"
C_GREEN = "#55A868"
C_ORG   = "#DD8452"

plt.rcParams.update({
    "figure.dpi"        : 150,
    "font.family"       : "DejaVu Sans",
    "axes.spines.top"   : False,
    "axes.spines.right" : False,
    "axes.grid"         : True,
    "grid.alpha"        : 0.3,
    "axes.titlesize"    : 13,
    "axes.titleweight"  : "bold",
    "axes.labelsize"    : 10,
})

def savefig(name):
    path = os.path.join(CHARTS_DIR, name)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {name}")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Revenue by Region (horizontal bar + margin % label)
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 1: Revenue by Region...")
df = pd.read_csv(os.path.join(DATA_DIR, "kpi_by_region.csv"))
df = df.sort_values("total_revenue", ascending=True)   # ascending so top = right

fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.barh(df["region"], df["total_revenue"], color=COLORS[:len(df)], height=0.5, zorder=3)

for bar, (_, row) in zip(bars, df.iterrows()):
    w = bar.get_width()
    ax.text(w + 2000, bar.get_y() + bar.get_height() / 2,
            f"${w:,.0f}   margin: {row['margin_pct']:.1f}%",
            va="center", fontsize=8.5)

ax.set_title("Total Revenue by Region (with profit margin %)")
ax.set_xlabel("Revenue ($)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
ax.set_xlim(0, df["total_revenue"].max() * 1.45)
savefig("chart1_revenue_by_region.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Revenue & Margin by Product Category (twin-axis grouped bar)
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 2: Revenue & Margin by Category...")
df = pd.read_csv(os.path.join(DATA_DIR, "kpi_by_category.csv"))

x     = range(len(df))
width = 0.35

fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()

bars1 = ax1.bar([i - width/2 for i in x], df["total_revenue"],
                width=width, color=C_BLUE, label="Revenue", zorder=3)
bars2 = ax2.bar([i + width/2 for i in x], df["margin_pct"],
                width=width, color=C_GREEN, alpha=0.85, label="Margin %", zorder=3)

# Value labels
for bar in bars1:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
             f"${bar.get_height()/1000:.0f}K", ha="center", fontsize=8, color=C_BLUE)
for bar in bars2:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f"{bar.get_height():.1f}%", ha="center", fontsize=8, color=C_GREEN)

ax1.set_xticks(list(x))
ax1.set_xticklabels(df["category"])
ax1.set_ylabel("Total Revenue ($)", color=C_BLUE)
ax2.set_ylabel("Profit Margin (%)", color=C_GREEN)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))
ax1.set_title("Revenue & Profit Margin by Product Category")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="upper right")

ax2.spines["top"].set_visible(False)
savefig("chart2_margin_by_category.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Top 10 Sub-categories (revenue bar + profit dot)
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 3: Top 10 Sub-Categories...")
df = pd.read_csv(os.path.join(DATA_DIR, "kpi_by_subcategory.csv"))
df = df.sort_values("total_revenue", ascending=True)

# Colour bars by profit (green = positive, red = negative)
bar_colors = [C_GREEN if p > 0 else C_RED for p in df["total_profit"]]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(df["sub_category"], df["total_revenue"],
               color=bar_colors, height=0.55, zorder=3)

# Profit label on each bar
for bar, (_, row) in zip(bars, df.iterrows()):
    w = bar.get_width()
    profit_str = f"  profit: ${row['total_profit']:,.0f}"
    color = C_GREEN if row["total_profit"] > 0 else C_RED
    ax.text(w + 500, bar.get_y() + bar.get_height()/2,
            profit_str, va="center", fontsize=8, color=color)

ax.set_title("Top 10 Sub-Categories by Revenue\n(green = profitable, red = loss-making)")
ax.set_xlabel("Total Revenue ($)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))
ax.set_xlim(0, df["total_revenue"].max() * 1.45)
savefig("chart3_top_subcategories.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Revenue by Customer Segment (donut)
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 4: Revenue by Segment...")
df = pd.read_csv(os.path.join(DATA_DIR, "kpi_by_segment.csv"))

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    df["total_revenue"],
    labels=df["segment"],
    autopct="%1.1f%%",
    colors=COLORS[:len(df)],
    startangle=90,
    pctdistance=0.78,
    wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),  # donut
)
for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight("bold")

# Centre label showing total revenue
total = df["total_revenue"].sum()
ax.text(0, 0, f"${total/1e6:.2f}M\ntotal", ha="center", va="center",
        fontsize=11, fontweight="bold")

ax.set_title("Revenue Share by Customer Segment", pad=20)
savefig("chart4_segment_donut.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Discount Band vs Profit Margin (the key insight chart)
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 5: Discount vs Margin...")
df = pd.read_csv(os.path.join(DATA_DIR, "kpi_by_discount.csv"))

# Clean up the label for display
df["label"] = df["discount_band"].str[4:]   # drop leading sort char

bar_colors = [C_GREEN if m > 0 else C_RED for m in df["margin_pct"]]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(df["label"], df["margin_pct"],
              color=bar_colors, width=0.5, zorder=3)

# Horizontal zero line
ax.axhline(0, color="black", linewidth=0.8, alpha=0.4)

for bar in bars:
    h = bar.get_height()
    offset = 0.4 if h >= 0 else -1.2
    ax.text(bar.get_x() + bar.get_width()/2, h + offset,
            f"{h:.1f}%", ha="center", fontsize=9, fontweight="bold",
            color=C_GREEN if h >= 0 else C_RED)

ax.set_title("How Discounting Destroys Margin\n(profit margin % by discount band)")
ax.set_ylabel("Profit Margin (%)")
ax.set_xlabel("Discount Band")

# Annotation arrow pointing to the high-discount bar
worst = df["margin_pct"].min()
worst_label = df.loc[df["margin_pct"].idxmin(), "label"]
ax.annotate(
    "High discounts\ndrive losses",
    xy=(df[df["label"] == worst_label].index[0] - df.index[0], worst),
    xytext=(2.5, worst / 2),
    arrowprops=dict(arrowstyle="->", color="black", lw=1),
    fontsize=9, ha="center",
)

savefig("chart5_discount_vs_margin.png")

print("\nAll 5 charts saved to charts/")

"""
02_analyse.py
-------------
Analyses the clean campaign data and creates 4 charts.

KPIs calculated:
- CTR  (Click-Through Rate)  = Clicks / Impressions * 100
- CAC  (Cost per Enrollment) = Total Cost / Total Enrollments
- ROAS (Return on Ad Spend)  = Total Revenue / Total Cost

Charts saved to outputs/charts/:
- chart1_ctr_by_platform.png
- chart2_roas_by_platform.png
- chart3_cac_by_platform.png
- chart4_monthly_spend.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# --- File paths ---
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE  = os.path.join(BASE_DIR, "data", "campaigns_clean.csv")
CHARTS_DIR  = os.path.join(BASE_DIR, "charts")

# Create charts folder if it doesn't exist yet
os.makedirs(CHARTS_DIR, exist_ok=True)

# --- Load clean data ---
print("Loading clean data...")
df = pd.read_csv(CLEAN_FILE, parse_dates=["date"])
print(f"{len(df)} rows loaded.\n")

# ================================================================
# STEP 1 — Calculate KPIs by Platform
# ================================================================
# We group by platform and sum up all the raw numbers first,
# then calculate ratios. This gives accurate results.

platform_data = df.groupby("platform").agg(
    impressions  = ("impressions", "sum"),
    clicks       = ("clicks",      "sum"),
    enrollments  = ("enrollments", "sum"),
    cost         = ("cost",        "sum"),
    revenue      = ("revenue",     "sum"),
).reset_index()

# Calculate KPIs
platform_data["CTR"]  = (platform_data["clicks"] / platform_data["impressions"] * 100).round(2)
platform_data["CAC"]  = (platform_data["cost"] / platform_data["enrollments"]).round(2)
platform_data["ROAS"] = (platform_data["revenue"] / platform_data["cost"]).round(2)

print("KPIs by Platform:")
print(platform_data[["platform", "CTR", "CAC", "ROAS"]].to_string(index=False))

# ================================================================
# STEP 2 — Monthly spend (for the trend chart)
# ================================================================
df["month"] = df["date"].dt.to_period("M")
monthly_spend = df.groupby("month")["cost"].sum().reset_index()
monthly_spend["month"] = monthly_spend["month"].astype(str)

# ================================================================
# STEP 3 — Chart settings
# ================================================================
# A consistent color palette and style for all charts
COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

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

# ================================================================
# CHART 1 — CTR by Platform
# ================================================================
print("\nCreating Chart 1: CTR by Platform...")

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    platform_data["platform"],
    platform_data["CTR"],
    color=COLORS,
    width=0.5,
    zorder=3,
)

# Add value labels on top of each bar
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.03,
        f"{height:.2f}%",
        ha="center", va="bottom", fontsize=9, fontweight="bold"
    )

ax.set_title("Click-Through Rate (CTR) by Platform")
ax.set_ylabel("CTR (%)")
ax.set_xlabel("Platform")
ax.set_ylim(0, platform_data["CTR"].max() * 1.2)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart1_ctr_by_platform.png"))
plt.close()
print("  Saved: chart1_ctr_by_platform.png")

# ================================================================
# CHART 2 — ROAS by Platform
# ================================================================
print("Creating Chart 2: ROAS by Platform...")

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    platform_data["platform"],
    platform_data["ROAS"],
    color=COLORS,
    width=0.5,
    zorder=3,
)

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.1,
        f"{height:.2f}x",
        ha="center", va="bottom", fontsize=9, fontweight="bold"
    )

# A dotted line at ROAS = 1 (break-even point)
ax.axhline(y=1, color="red", linestyle="--", linewidth=1, alpha=0.5, label="Break-even (1x)")
ax.legend(frameon=False)

ax.set_title("Return on Ad Spend (ROAS) by Platform")
ax.set_ylabel("ROAS (x)")
ax.set_xlabel("Platform")
ax.set_ylim(0, platform_data["ROAS"].max() * 1.2)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart2_roas_by_platform.png"))
plt.close()
print("  Saved: chart2_roas_by_platform.png")

# ================================================================
# CHART 3 — CAC by Platform
# ================================================================
print("Creating Chart 3: CAC by Platform...")

# Sort ascending so the cheapest platform is on the left
platform_cac = platform_data.sort_values("CAC", ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    platform_cac["platform"],
    platform_cac["CAC"],
    color=COLORS,
    width=0.5,
    zorder=3,
)

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 1,
        f"₹{height:,.0f}",
        ha="center", va="bottom", fontsize=9, fontweight="bold"
    )

ax.set_title("Cost per Enrollment (CAC) by Platform\n(lower is better)")
ax.set_ylabel("CAC (₹)")
ax.set_xlabel("Platform")
ax.set_ylim(0, platform_cac["CAC"].max() * 1.25)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart3_cac_by_platform.png"))
plt.close()
print("  Saved: chart3_cac_by_platform.png")

# ================================================================
# CHART 4 — Monthly Spend Trend
# ================================================================
print("Creating Chart 4: Monthly Spend Trend...")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    monthly_spend["month"],
    monthly_spend["cost"],
    color="#4C72B0",
    linewidth=2,
    marker="o",
    markersize=4,
)

# Shade under the line
ax.fill_between(
    monthly_spend["month"],
    monthly_spend["cost"],
    alpha=0.1,
    color="#4C72B0",
)

ax.set_title("Monthly Ad Spend Over Time")
ax.set_ylabel("Spend (₹)")
ax.set_xlabel("Month")

# Format y-axis to show values in lakhs (easier to read)
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"₹{x/100000:.1f}L")
)

# Rotate x-axis labels so they don't overlap
plt.xticks(rotation=45, ha="right", fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart4_monthly_spend.png"))
plt.close()
print("  Saved: chart4_monthly_spend.png")

# ================================================================
# Done
# ================================================================
print("\nAll 4 charts saved to outputs/charts/")
"""
03_stats_ab.py
--------------
Two things this script does:

1. BASIC STATS — mean, median, std, min, max for key metrics per platform
2. A/B TEST   — checks if the CTR difference between the top 2 platforms
                (by impressions) is statistically significant or just chance

What is an A/B test?
- We pick two platforms and ask: is Platform A's CTR actually better than
  Platform B's, or could this difference just be random noise?
- We use a Z-test to answer this. If p-value < 0.05, the difference is real.

Output: outputs/charts/chart5_ab_test.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats

# --- File paths ---
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE = os.path.join(BASE_DIR, "data", "campaigns_clean.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# --- Load data ---
print("Loading clean data...")
df = pd.read_csv(CLEAN_FILE, parse_dates=["date"])
print(f"{len(df)} rows loaded.\n")

# ================================================================
# PART 1 — Basic Stats per Platform
# ================================================================
print("=" * 50)
print("BASIC STATS PER PLATFORM")
print("=" * 50)

# Calculate CTR for each row first
df["ctr"] = df["clicks"] / df["impressions"] * 100

# Now get basic stats grouped by platform
stats_table = df.groupby("platform")["ctr"].agg(
    Mean  = "mean",
    Median= "median",
    Std   = "std",
    Min   = "min",
    Max   = "max",
).round(3)

print(stats_table)
print()

# ================================================================
# PART 2 — A/B Test
# ================================================================
print("=" * 50)
print("A/B TEST — CTR")
print("=" * 50)

# Step 1: Find top 2 platforms by total impressions (most data = most reliable)
top2 = (
    df.groupby("platform")["impressions"]
    .sum()
    .sort_values(ascending=False)
    .head(2)
    .index.tolist()
)

platform_a = top2[0]
platform_b = top2[1]
print(f"\nComparing: [{platform_a}] vs [{platform_b}]")
print(f"(Selected because they have the most impressions — most data to work with)\n")

# Step 2: Get CTR values for each platform (one CTR value per row/day)
ctr_a = df[df["platform"] == platform_a]["ctr"].values
ctr_b = df[df["platform"] == platform_b]["ctr"].values

print(f"{platform_a} — avg CTR: {ctr_a.mean():.3f}%  |  rows: {len(ctr_a)}")
print(f"{platform_b} — avg CTR: {ctr_b.mean():.3f}%  |  rows: {len(ctr_b)}")

# Step 3: Run the Z-test
# H0 (null hypothesis):     The two platforms have the same CTR
# H1 (alternate hypothesis): The CTRs are different
z_stat, p_value = stats.ttest_ind(ctr_a, ctr_b)  # ttest_ind gives us the same result here

print(f"\nZ-statistic : {z_stat:.4f}")
print(f"P-value     : {p_value:.4f}")

ALPHA = 0.05
if p_value < ALPHA:
    winner = platform_a if ctr_a.mean() > ctr_b.mean() else platform_b
    print(f"\nResult: SIGNIFICANT (p < {ALPHA})")
    print(f"→ {winner} has a statistically higher CTR. The difference is real, not random.")
else:
    print(f"\nResult: NOT SIGNIFICANT (p >= {ALPHA})")
    print(f"→ No meaningful CTR difference between the two platforms.")

# ================================================================
# PART 3 — Chart: Side-by-side CTR comparison
# ================================================================
print("\nCreating chart...")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle(f"A/B Test: {platform_a} vs {platform_b} — CTR", fontsize=13, fontweight="bold")

COLOR_A = "#4C72B0"
COLOR_B = "#DD8452"

# --- Left plot: Bar chart of average CTR ---
ax1 = axes[0]
bars = ax1.bar(
    [platform_a, platform_b],
    [ctr_a.mean(), ctr_b.mean()],
    color=[COLOR_A, COLOR_B],
    width=0.4,
    zorder=3,
)

for bar in bars:
    height = bar.get_height()
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.02,
        f"{height:.3f}%",
        ha="center", va="bottom", fontsize=10, fontweight="bold"
    )

# Show p-value result on the chart
result_text = f"p = {p_value:.4f}  →  {'Significant ✓' if p_value < ALPHA else 'Not significant ✗'}"
ax1.set_title(f"Average CTR\n{result_text}", fontsize=10)
ax1.set_ylabel("CTR (%)")
ax1.set_ylim(0, max(ctr_a.mean(), ctr_b.mean()) * 1.25)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.grid(axis="y", alpha=0.3)

# --- Right plot: Box plot to show spread of CTR values ---
ax2 = axes[1]
bp = ax2.boxplot(
    [ctr_a, ctr_b],
    tick_labels=[platform_a, platform_b],
    patch_artist=True,
    widths=0.4,
    medianprops=dict(color="black", linewidth=2),
)

bp["boxes"][0].set_facecolor(COLOR_A)
bp["boxes"][1].set_facecolor(COLOR_B)
for box in bp["boxes"]:
    box.set_alpha(0.7)

ax2.set_title("CTR Distribution (Box Plot)\nShows spread of daily CTR values", fontsize=10)
ax2.set_ylabel("CTR (%)")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.grid(axis="y", alpha=0.3)

plt.tight_layout()
chart_path = os.path.join(CHARTS_DIR, "chart5_ab_test.png")
plt.savefig(chart_path)
plt.close()

print(f"Saved: chart5_ab_test.png")
print("\nDone.")

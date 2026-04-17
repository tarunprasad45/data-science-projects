"""
analyse.py
----------
Analyses customer behaviour data and creates 4 charts.

Charts:
1. Average Total Spend by Membership Type
2. Customer Satisfaction Breakdown
3. Spend vs Items Purchased (scatter plot)
4. Does Discount Affect Spend?

Input : data/customers_clean.csv
Output: charts/chart1_spend_by_membership.png
        charts/chart2_satisfaction.png
        charts/chart3_spend_vs_items.png
        charts/chart4_discount_effect.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# --- File paths ---
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE = os.path.join(BASE_DIR, "data", "customers_clean.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# --- Load ---
print("Loading clean data...")
df = pd.read_csv(CLEAN_FILE)
print(f"{len(df)} rows loaded.\n")

# --- Chart style ---
COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]
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
# CHART 1 — Avg Spend by Membership Type
# ================================================================
print("Creating Chart 1: Spend by Membership Type...")

# Order: Gold → Silver → Bronze (high to low value)
order = ["Gold", "Silver", "Bronze"]
spend_by_membership = (
    df.groupby("membership_type")["total_spend"]
    .mean()
    .reindex(order)
    .round(2)
)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(spend_by_membership.index, spend_by_membership.values,
              color=["#FFD700", "#C0C0C0", "#CD7F32"], width=0.45, zorder=3)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 10,
            f"${height:,.0f}", ha="center", va="bottom",
            fontsize=10, fontweight="bold")

ax.set_title("Average Total Spend by Membership Type")
ax.set_ylabel("Avg Spend ($)")
ax.set_xlabel("Membership Type")
ax.set_ylim(0, spend_by_membership.max() * 1.2)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart1_spend_by_membership.png"))
plt.close()
print("  Saved: chart1_spend_by_membership.png")

# ================================================================
# CHART 2 — Satisfaction Breakdown
# ================================================================
print("Creating Chart 2: Satisfaction Breakdown...")

sat_counts = df["satisfaction"].value_counts()

# Use a consistent color per label
sat_colors = {
    "Satisfied"  : "#55A868",
    "Neutral"    : "#DD8452",
    "Unsatisfied": "#C44E52",
    "Unknown"    : "#AAAAAA",
}
colors = [sat_colors.get(label, "#999999") for label in sat_counts.index]

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    sat_counts.values,
    labels=sat_counts.index,
    autopct="%1.1f%%",
    colors=colors,
    startangle=140,
    pctdistance=0.75,
    wedgeprops=dict(edgecolor="white", linewidth=2),
)
for text in autotexts:
    text.set_fontsize(10)
    text.set_fontweight("bold")

ax.set_title("Customer Satisfaction Breakdown", pad=20)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart2_satisfaction.png"))
plt.close()
print("  Saved: chart2_satisfaction.png")

# ================================================================
# CHART 3 — Spend vs Items Purchased (scatter)
# ================================================================
print("Creating Chart 3: Spend vs Items Purchased...")

# Colour each dot by membership type
membership_colors = {"Gold": "#FFD700", "Silver": "#A0A0A0", "Bronze": "#CD7F32"}
color_list = df["membership_type"].map(membership_colors)

fig, ax = plt.subplots(figsize=(9, 6))
scatter = ax.scatter(
    df["items_purchased"],
    df["total_spend"],
    c=color_list,
    alpha=0.7,
    edgecolors="white",
    linewidths=0.5,
    s=60,
    zorder=3,
)

# Manual legend for membership colours
legend_handles = [
    mpatches.Patch(color="#FFD700", label="Gold"),
    mpatches.Patch(color="#A0A0A0", label="Silver"),
    mpatches.Patch(color="#CD7F32", label="Bronze"),
]
ax.legend(handles=legend_handles, title="Membership", frameon=False, loc="upper left")

ax.set_title("Total Spend vs Items Purchased\n(coloured by Membership Type)")
ax.set_xlabel("Items Purchased")
ax.set_ylabel("Total Spend ($)")

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart3_spend_vs_items.png"))
plt.close()
print("  Saved: chart3_spend_vs_items.png")

# ================================================================
# CHART 4 — Does Discount Affect Spend?
# ================================================================
print("Creating Chart 4: Discount Effect on Spend...")

discount_spend = df.groupby("discount_applied")["total_spend"].mean().round(2)

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(
    ["No Discount", "Discount Applied"],
    [discount_spend.get("No", 0), discount_spend.get("Yes", 0)],
    color=["#4C72B0", "#55A868"],
    width=0.4,
    zorder=3,
)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 5,
            f"${height:,.0f}", ha="center", va="bottom",
            fontsize=10, fontweight="bold")

ax.set_title("Does Applying a Discount Affect Average Spend?")
ax.set_ylabel("Avg Total Spend ($)")
ax.set_ylim(0, max(discount_spend.values) * 1.25)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart4_discount_effect.png"))
plt.close()
print("  Saved: chart4_discount_effect.png")

print("\nAll 4 charts saved to charts/")

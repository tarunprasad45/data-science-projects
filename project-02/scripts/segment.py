"""
segment.py
----------
Groups customers into 3 segments using KMeans clustering.

Features used for clustering:
- total_spend          : how much they spend
- items_purchased      : how many items they buy
- days_since_purchase  : how recently they bought (recency)

Why these 3? They capture the core of customer behaviour —
how valuable, how active, and how recent each customer is.

After clustering, we label each segment in plain English:
- High Value    : spends a lot, buys often, bought recently
- Occasional    : mid-range spend, moderate activity
- At Risk       : low spend, hasn't bought in a while

Output: charts/chart5_customer_segments.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- File paths ---
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE = os.path.join(BASE_DIR, "data", "customers_clean.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# --- Load ---
print("Loading clean data...")
df = pd.read_csv(CLEAN_FILE)
print(f"{len(df)} rows loaded.\n")

# ================================================================
# STEP 1 — Pick features and scale them
# ================================================================
# We use 3 columns for clustering
features = ["total_spend", "items_purchased", "days_since_purchase"]
X = df[features].copy()

# StandardScaler makes sure no single feature dominates
# (e.g. spend in hundreds vs days in tens)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("Features scaled.")

# ================================================================
# STEP 2 — KMeans clustering (3 clusters)
# ================================================================
# n_clusters=3 means we want 3 groups
# random_state=42 means results are reproducible every time you run it
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X_scaled)
print("Clustering done.")

# ================================================================
# STEP 3 — Label each cluster in plain English
# ================================================================
# Look at the average spend and recency per cluster to decide the label
cluster_summary = df.groupby("cluster").agg(
    avg_spend         = ("total_spend",       "mean"),
    avg_items         = ("items_purchased",   "mean"),
    avg_days          = ("days_since_purchase","mean"),
    count             = ("customer_id",        "count"),
).round(2)

print("\nCluster Summary (before labelling):")
print(cluster_summary)

# Assign labels based on spend rank
# Highest avg spend = High Value, lowest = At Risk
spend_rank = cluster_summary["avg_spend"].rank(ascending=False)
label_map = {}
for cluster_id, rank in spend_rank.items():
    if rank == 1:
        label_map[cluster_id] = "High Value"
    elif rank == 2:
        label_map[cluster_id] = "Occasional"
    else:
        label_map[cluster_id] = "At Risk"

df["segment"] = df["cluster"].map(label_map)

# Print final segment summary
segment_summary = df.groupby("segment").agg(
    customers         = ("customer_id",        "count"),
    avg_spend         = ("total_spend",        "mean"),
    avg_items         = ("items_purchased",    "mean"),
    avg_days_inactive = ("days_since_purchase","mean"),
).round(2)

print("\nFinal Segment Summary:")
print(segment_summary)

# ================================================================
# STEP 4 — Chart: Scatter plot coloured by segment
# ================================================================
print("\nCreating chart...")

SEGMENT_COLORS = {
    "High Value": "#55A868",
    "Occasional": "#DD8452",
    "At Risk"   : "#C44E52",
}

fig, ax = plt.subplots(figsize=(9, 6))

for segment, group in df.groupby("segment"):
    ax.scatter(
        group["items_purchased"],
        group["total_spend"],
        label=segment,
        color=SEGMENT_COLORS[segment],
        alpha=0.75,
        edgecolors="white",
        linewidths=0.5,
        s=65,
        zorder=3,
    )

ax.set_title("Customer Segments — Spend vs Items Purchased\n(KMeans Clustering, 3 Segments)")
ax.set_xlabel("Items Purchased")
ax.set_ylabel("Total Spend ($)")
ax.legend(title="Segment", frameon=False, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "chart5_customer_segments.png"))
plt.close()

print("Saved: chart5_customer_segments.png")
print("\nDone.")

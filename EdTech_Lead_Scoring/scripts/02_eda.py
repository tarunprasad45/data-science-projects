"""
02_eda.py
---------
Exploratory Data Analysis on the cleaned leads dataset.
Answers the business question: what does a converting lead look like?

Charts:
  chart1_conversion_by_source.png     — lead source vs conversion rate
  chart2_conversion_by_activity.png   — last activity vs conversion rate
  chart3_time_on_site_dist.png        — time on site distribution (converters vs not)
  chart4_occupation_conversion.png    — occupation breakdown and conversion rate

Each chart is framed as a business insight, not just a distribution.

Input : data/leads_clean.csv
Output: charts/ (4 charts)
        data/eda_source.csv
        data/eda_activity.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE = os.path.join(BASE_DIR, "data", "leads_clean.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
DATA_DIR   = os.path.join(BASE_DIR, "data")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading clean data...")
df = pd.read_csv(CLEAN_FILE)
df['Converted'] = df['Converted'].astype(int)
print(f"{len(df):,} rows loaded.\n")

# ── Style ─────────────────────────────────────────────────────────────────────
C_BLUE  = "#4C72B0"
C_GREEN = "#55A868"
C_RED   = "#C44E52"
C_ORG   = "#DD8452"
COLORS  = [C_BLUE, C_ORG, C_GREEN, C_RED, "#8172B2", "#937860"]

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
# CHART 1 — Conversion Rate by Lead Source
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 1: Conversion by Lead Source...")

source_kpi = (
    df.groupby('Lead Source')
    .agg(total=('Converted', 'count'), converted=('Converted', 'sum'))
    .reset_index()
)
source_kpi['conv_rate'] = (source_kpi['converted'] / source_kpi['total'] * 100).round(1)
source_kpi = source_kpi[source_kpi['total'] >= 50]  # filter tiny sources
source_kpi = source_kpi.sort_values('conv_rate', ascending=True)
source_kpi.to_csv(os.path.join(DATA_DIR, 'eda_source.csv'), index=False)

bar_colors = [C_GREEN if r == source_kpi['conv_rate'].max() else
              C_RED   if r == source_kpi['conv_rate'].min() else
              C_BLUE  for r in source_kpi['conv_rate']]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(source_kpi['Lead Source'], source_kpi['conv_rate'],
               color=bar_colors, height=0.55, zorder=3)

for bar, (_, row) in zip(bars, source_kpi.iterrows()):
    w = bar.get_width()
    ax.text(w + 0.4, bar.get_y() + bar.get_height()/2,
            f"{w:.1f}%  (n={row['total']:,})", va='center', fontsize=8.5)

ax.set_title("Lead Conversion Rate by Source\n(min 50 leads; green = best, red = worst)")
ax.set_xlabel("Conversion Rate (%)")
ax.set_xlim(0, source_kpi['conv_rate'].max() * 1.4)
savefig("chart1_conversion_by_source.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Conversion Rate by Last Activity
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 2: Conversion by Last Activity...")

if 'Last Activity' in df.columns:
    activity_kpi = (
        df.groupby('Last Activity')
        .agg(total=('Converted', 'count'), converted=('Converted', 'sum'))
        .reset_index()
    )
    activity_kpi['conv_rate'] = (activity_kpi['converted'] / activity_kpi['total'] * 100).round(1)
    activity_kpi = activity_kpi[activity_kpi['total'] >= 30]
    activity_kpi = activity_kpi.sort_values('conv_rate', ascending=True)
    activity_kpi.to_csv(os.path.join(DATA_DIR, 'eda_activity.csv'), index=False)

    bar_colors = [C_GREEN if r >= 70 else C_RED if r <= 20 else C_BLUE
                  for r in activity_kpi['conv_rate']]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(activity_kpi['Last Activity'], activity_kpi['conv_rate'],
                   color=bar_colors, height=0.55, zorder=3)

    for bar, (_, row) in zip(bars, activity_kpi.iterrows()):
        w = bar.get_width()
        ax.text(w + 0.4, bar.get_y() + bar.get_height()/2,
                f"{w:.1f}%  (n={row['total']:,})", va='center', fontsize=8)

    ax.set_title("Conversion Rate by Last Activity\n(green ≥70%, red ≤20%)")
    ax.set_xlabel("Conversion Rate (%)")
    ax.set_xlim(0, activity_kpi['conv_rate'].max() * 1.4)
    savefig("chart2_conversion_by_activity.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Time on Site: Converters vs Non-Converters
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 3: Time on Site Distribution...")

if 'Time on Site' in df.columns:
    converted     = df[df['Converted'] == 1]['Time on Site'].dropna()
    not_converted = df[df['Converted'] == 0]['Time on Site'].dropna()

    fig, ax = plt.subplots(figsize=(10, 5))

    bins = np.linspace(0, df['Time on Site'].quantile(0.97), 40)
    ax.hist(not_converted.clip(upper=df['Time on Site'].quantile(0.97)),
            bins=bins, alpha=0.6, color=C_RED, label='Not Converted', density=True)
    ax.hist(converted.clip(upper=df['Time on Site'].quantile(0.97)),
            bins=bins, alpha=0.6, color=C_GREEN, label='Converted', density=True)

    # Median lines
    ax.axvline(converted.median(), color=C_GREEN, linestyle='--', linewidth=1.5,
               label=f'Converted median: {converted.median():.0f}s')
    ax.axvline(not_converted.median(), color=C_RED, linestyle='--', linewidth=1.5,
               label=f'Not converted median: {not_converted.median():.0f}s')

    ax.set_title("Time on Site — Converters vs Non-Converters\n(density; clipped at 97th percentile)")
    ax.set_xlabel("Time on Site (seconds)")
    ax.set_ylabel("Density")
    ax.legend(frameon=False, fontsize=9)
    savefig("chart3_time_on_site_dist.png")

    print(f"  Median time — Converted: {converted.median():.0f}s | Not converted: {not_converted.median():.0f}s")
    print(f"  Gap: {converted.median() - not_converted.median():.0f}s")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Occupation: Volume + Conversion Rate
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 4: Occupation Breakdown...")

if 'Occupation' in df.columns:
    occ_kpi = (
        df.groupby('Occupation')
        .agg(total=('Converted', 'count'), converted=('Converted', 'sum'))
        .reset_index()
    )
    occ_kpi['conv_rate'] = (occ_kpi['converted'] / occ_kpi['total'] * 100).round(1)
    occ_kpi = occ_kpi.sort_values('total', ascending=False)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    x     = np.arange(len(occ_kpi))
    width = 0.38

    bars1 = ax1.bar(x - width/2, occ_kpi['total'], width=width,
                    color=C_BLUE, label='Total Leads', zorder=3)
    bars2 = ax2.bar(x + width/2, occ_kpi['conv_rate'], width=width,
                    color=C_GREEN, alpha=0.85, label='Conversion Rate %', zorder=3)

    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                 f"{bar.get_height():,.0f}", ha='center', fontsize=8, color=C_BLUE)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
                 f"{bar.get_height():.1f}%", ha='center', fontsize=8, color=C_GREEN)

    ax1.set_xticks(x)
    ax1.set_xticklabels(occ_kpi['Occupation'], rotation=15, ha='right')
    ax1.set_ylabel("Total Leads", color=C_BLUE)
    ax2.set_ylabel("Conversion Rate (%)", color=C_GREEN)
    ax2.spines['top'].set_visible(False)
    ax1.set_title("Lead Volume and Conversion Rate by Occupation")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')

    savefig("chart4_occupation_conversion.png")

print("\nAll EDA charts saved.")
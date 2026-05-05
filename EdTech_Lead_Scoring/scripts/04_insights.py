"""
04_insights.py
--------------
Translates model outputs into business-facing charts and a summary card.

Charts:
  chart8_lead_tier_distribution.png  — Hot/Warm/Cold breakdown vs actual conversion
  chart9_score_vs_actual.png         — score distribution: do high scorers actually convert?
  chart10_kpi_summary.png            — single-page KPI card for portfolio/presentation

Business framing:
  The model produces a 0–100 lead score. We bucket into 3 tiers:
    Hot  (65–100): prioritise immediately — high sales effort
    Warm (40–65) : nurture sequence — automated comms
    Cold (0–40)  : low effort — drip content only

  This directly maps to sales team prioritisation: instead of treating
  all 9,240 leads equally, the team works the top 30% with 80% of
  effort — reproducing the notebook's target of ~80% conversion on
  prioritised leads.

Input : data/lead_scores.csv, data/model_metrics.csv
Output: charts/ (3 charts)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORES_FILE = os.path.join(BASE_DIR, "data", "lead_scores.csv")
METRICS_FILE= os.path.join(BASE_DIR, "data", "model_metrics.csv")
CHARTS_DIR  = os.path.join(BASE_DIR, "charts")

C_BLUE  = "#4C72B0"
C_GREEN = "#55A868"
C_RED   = "#C44E52"
C_ORG   = "#DD8452"
C_GOLD  = "#E8B84B"

plt.rcParams.update({
    "figure.dpi": 150, "font.family": "DejaVu Sans",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.3,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.labelsize": 10,
})

def savefig(name):
    path = os.path.join(CHARTS_DIR, name)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {name}")

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading scored leads...")
scores  = pd.read_csv(SCORES_FILE)
metrics = pd.read_csv(METRICS_FILE).iloc[0]
print(f"{len(scores):,} leads loaded.\n")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 8 — Lead Tier Distribution vs Actual Conversion
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 8: Lead Tier Distribution...")

tier_order = ['Hot', 'Warm', 'Cold']
tier_kpi = (
    scores.groupby('lead_tier', observed=True)
    .agg(total=('actual', 'count'), converted=('actual', 'sum'))
    .reindex(tier_order)
    .reset_index()
)
tier_kpi['conv_rate'] = (tier_kpi['converted'] / tier_kpi['total'] * 100).round(1)
tier_kpi['pct_of_leads'] = (tier_kpi['total'] / len(scores) * 100).round(1)

print(tier_kpi.to_string(index=False))

tier_colors = {'Hot': C_RED, 'Warm': C_ORG, 'Cold': C_BLUE}

fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()

x     = np.arange(len(tier_kpi))
width = 0.38

bars1 = ax1.bar(x - width/2, tier_kpi['total'], width=width,
                color=[tier_colors[t] for t in tier_kpi['lead_tier']],
                alpha=0.8, label='Total Leads in Tier', zorder=3)
bars2 = ax2.bar(x + width/2, tier_kpi['conv_rate'], width=width,
                color=C_GREEN, alpha=0.85, label='Actual Conversion Rate %', zorder=3)

for bar in bars1:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
             f"{bar.get_height():,.0f}", ha='center', fontsize=9)
for bar, (_, row) in zip(bars2, tier_kpi.iterrows()):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{bar.get_height():.1f}%", ha='center', fontsize=9, color=C_GREEN, fontweight='bold')

ax1.set_xticks(x)
ax1.set_xticklabels(tier_kpi['lead_tier'], fontsize=11)
ax1.set_ylabel("Number of Leads")
ax2.set_ylabel("Actual Conversion Rate (%)", color=C_GREEN)
ax2.spines['top'].set_visible(False)
ax1.set_title("Lead Tier Distribution vs Actual Conversion Rate\n(Hot = prioritise, Cold = drip only)")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')

savefig("chart8_lead_tier_distribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 9 — Score Distribution: Converters vs Non-Converters
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 9: Score vs Actual Conversion...")

converted     = scores[scores['actual'] == 1]['lead_score']
not_converted = scores[scores['actual'] == 0]['lead_score']

fig, ax = plt.subplots(figsize=(10, 5))
bins = np.linspace(0, 100, 30)
ax.hist(not_converted, bins=bins, alpha=0.55, color=C_RED,
        density=True, label='Not Converted')
ax.hist(converted, bins=bins, alpha=0.55, color=C_GREEN,
        density=True, label='Converted')

# Tier boundary lines
ax.axvline(40, color='gray', linestyle=':', linewidth=1.2, label='Cold/Warm boundary (40)')
ax.axvline(65, color='black', linestyle=':', linewidth=1.2, label='Warm/Hot boundary (65)')

ax.set_title("Lead Score Distribution — Converters vs Non-Converters\n(Good separation = model works)")
ax.set_xlabel("Lead Score (0–100)")
ax.set_ylabel("Density")
ax.legend(frameon=False, fontsize=9)

savefig("chart9_score_distribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 10 — KPI Summary Card
# ══════════════════════════════════════════════════════════════════════════════
print("Creating Chart 10: KPI Summary Card...")

hot_leads   = tier_kpi[tier_kpi['lead_tier'] == 'Hot']
hot_conv    = hot_leads['conv_rate'].values[0] if len(hot_leads) > 0 else 0
total_leads = len(scores)
baseline    = scores['actual'].mean() * 100
lift        = hot_conv / baseline if baseline > 0 else 0

kpis = [
    ("Total Leads Scored",         f"{total_leads:,}"),
    ("Baseline Conversion Rate",   f"{baseline:.1f}%"),
    ("Model Accuracy (Test Set)",  f"{metrics['accuracy']:.1f}%"),
    ("AUC Score",                  f"{metrics['auc']:.1f}%"),
    ("Sensitivity (Recall)",       f"{metrics['sensitivity']:.1f}%"),
    ("Specificity",                f"{metrics['specificity']:.1f}%"),
    ("Hot Lead Conv. Rate",        f"{hot_conv:.1f}%"),
    ("Conversion Lift (Hot tier)", f"{lift:.1f}×"),
]

fig, ax = plt.subplots(figsize=(11, 7))
ax.axis('off')

ax.text(0.5, 0.97, "EdTech Lead Scoring — Model KPI Summary",
        ha='center', va='top', fontsize=14, fontweight='bold', transform=ax.transAxes)
ax.text(0.5, 0.90,
        "X Education | 9,240 Leads | Logistic Regression + SMOTE + RFE + VIF Pruning",
        ha='center', va='top', fontsize=9, color='gray', transform=ax.transAxes)

cols   = 2
box_w, box_h = 0.44, 0.13
x_starts = [0.03, 0.52]
y_start  = 0.83

highlight_green = {2, 3, 6, 7}  # accuracy, AUC, hot conv, lift
highlight_red   = {4}           # sensitivity

for i, (label, value) in enumerate(kpis):
    col_i = i % cols
    row_i = i // cols
    x = x_starts[col_i]
    y = y_start - row_i * (box_h + 0.03)

    color = C_GREEN if i in highlight_green else \
            C_ORG   if i in highlight_red   else C_BLUE

    rect = mpatches.FancyBboxPatch(
        (x, y - box_h), box_w, box_h,
        boxstyle="round,pad=0.01",
        linewidth=1.5, edgecolor=color,
        facecolor=color + "15",
        transform=ax.transAxes,
    )
    ax.add_patch(rect)
    ax.text(x + box_w/2, y - 0.025, label,
            ha='center', va='top', fontsize=8.5, color='gray',
            transform=ax.transAxes)
    ax.text(x + box_w/2, y - box_h/2 - 0.01, value,
            ha='center', va='center', fontsize=12, fontweight='bold',
            color=color, transform=ax.transAxes)

savefig("chart10_kpi_summary.png")

print("\nAll insight charts saved.")
print(f"\nBusiness impact summary:")
print(f"  Baseline conversion: {baseline:.1f}%")
print(f"  Hot lead conversion: {hot_conv:.1f}%")
print(f"  Lift on Hot tier   : {lift:.1f}×")
print(f"  → Sales team focusing on Hot leads only would see ~{lift:.1f}x better conversion")
# Marketing Campaign Performance Analysis
**Portfolio Project | Python · Pandas · Matplotlib · SciPy**

---

## Overview

End-to-end analysis of a multi-platform digital marketing dataset covering **Jan 2024 – Oct 2025** (~22 months). Built a three-script Python pipeline to clean raw Excel data, compute KPIs, produce publication-ready charts, and run statistical significance testing.

---

## Pipeline

| Script | What it does |
|---|---|
| `clean.py` | Loads raw Excel, renames columns, drops nulls/duplicates, saves clean CSV |
| `02_analyse.py` | Aggregates by platform, calculates CTR / ROAS / CAC, generates 4 charts |
| `03_stats_ab.py` | Computes per-platform descriptive stats, runs A/B Z-test on CTR |

---

## Key Findings

### CTR by Platform
All five platforms (Facebook, Google Ads, Instagram, LinkedIn, YouTube) cluster tightly between **5.46% – 5.58%**, indicating consistent audience engagement across channels.

### ROAS by Platform
Every platform returns well above break-even. **LinkedIn leads at 25.45x**, followed by Instagram (24.01x), Facebook (23.46x), Google Ads (22.97x), and YouTube (22.13x).

### Cost per Enrollment (CAC)
**LinkedIn is the most cost-efficient at ₹219/enrollment**, despite its premium reputation — likely due to higher-intent professional audiences. Google Ads and YouTube are the priciest at ₹243.

### Monthly Spend Trend
Spend is broadly stable at ~₹35–40L/month with two notable spikes: **March 2024 (~₹70L)** and **August 2024 (~₹73L)**, and a peak in **May 2025 (~₹77L)**.

### A/B Test (Google Ads vs Facebook — CTR)
- Google Ads: **5.496%** | Facebook: **5.548%**
- p-value: **0.7304** → **Not statistically significant**
- The CTR difference between the two highest-impression platforms is attributable to random variation, not a true performance gap.

---

## Skills Demonstrated

- **Data wrangling** — Excel ingestion, column standardisation, null/duplicate handling with Pandas
- **KPI design** — Ratio metrics (CTR, ROAS, CAC) calculated on aggregated totals to avoid averaging bias
- **Data visualisation** — Consistent chart style, annotated bar charts, area line chart, box plots
- **Statistical testing** — Two-sample t-test / Z-test with hypothesis framing and p-value interpretation
- **Modular scripting** — Clean separation of cleaning, analysis, and stats into independent, reusable scripts

---

*Tools: Python 3, Pandas, Matplotlib, SciPy, openpyxl*

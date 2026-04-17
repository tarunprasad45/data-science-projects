# E-Commerce Customer Behaviour Analysis
**Portfolio Project | Python · Pandas · Matplotlib · Scikit-learn (KMeans)**

---

## Overview

End-to-end analysis of an e-commerce customer dataset. Built a three-script Python pipeline to clean raw data, compute behavioural KPIs, produce charts, and apply unsupervised machine learning to segment customers into actionable groups.

The goal was to answer three business questions: *Who spends the most? How satisfied are customers? And can we identify distinct customer types from behaviour alone?*

---

## Pipeline

| Script | What it does |
|---|---|
| `clean.py` | Loads raw CSV, standardises column names, fills 2 missing satisfaction values with `'Unknown'` instead of dropping rows, converts boolean discount flags to readable Yes/No |
| `analyse.py` | Computes spend by membership tier, satisfaction distribution, spend-vs-items scatter, and discount effect — outputs 4 charts |
| `segment.py` | Runs KMeans clustering (k=3) on spend, items purchased, and recency; labels clusters in plain English; outputs segmentation chart |

---

## Key Findings

### Spend by Membership Tier
Gold members spend nearly **3× more than Bronze** on average ($1,311 vs $473), with Silver in the middle at $748. This confirms membership tier is a strong predictor of customer value — the loyalty programme is working as intended.

### Customer Satisfaction
Satisfaction is surprisingly fragmented: only **35.7% are Satisfied**, while **33.1% are Unsatisfied** and 30.6% are Neutral. The near-even three-way split is a red flag — close to two-thirds of customers are not actively happy. This suggests a retention or product-experience issue worth investigating further.

### Spend vs Items Purchased
The scatter plot (coloured by membership) reveals **three visually distinct bands** corresponding to Gold, Silver, and Bronze — confirming that membership tier cleanly separates spending behaviour. There's also a clear positive relationship between items purchased and total spend within each tier.

### Discount Effect on Spend
Counter-intuitively, customers **without a discount applied average $903**, compared to $787 for those with a discount. One explanation: higher-value customers (Gold tier) may purchase without needing discounts, pulling the no-discount average up. This is a confounding variable worth controlling for before drawing conclusions.

### KMeans Customer Segmentation
Using three features — total spend, items purchased, and days since last purchase — KMeans identified three distinct segments:

- **High Value** — high spend, frequent purchases, recently active
- **Occasional** — mid-range spend, moderate activity
- **At Risk** — lower spend, hasn't purchased recently

The scatter plot shows clean cluster separation, validating that these three features together are sufficient to meaningfully distinguish customer types. This kind of segmentation can directly inform targeted re-engagement or upsell campaigns.

---

## Skills Demonstrated

- **Data cleaning** — handling missing values with domain-appropriate imputation (fill vs drop), type conversion, duplicate detection
- **Exploratory analysis** — bar charts, pie charts, and scatter plots to surface patterns across multiple dimensions
- **Unsupervised ML** — StandardScaler normalisation before KMeans to prevent feature dominance; cluster labelling from summary statistics
- **Business interpretation** — translating model outputs into actionable segment labels rather than reporting raw cluster IDs
- **Modular pipeline design** — clean separation of cleaning, analysis, and modelling into independent scripts

---

*Tools: Python 3, Pandas, Matplotlib, Scikit-learn*


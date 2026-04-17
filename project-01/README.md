# 📊 Marketing Campaign Analytics Project

A complete data analysis project that evaluates marketing campaign performance across multiple platforms using real-world KPIs like CTR, CAC, and ROAS.

---

## 🚀 What This Project Does

This project takes raw campaign data → cleans it → analyzes it → produces insights and visualizations.

### Pipeline:

1. **Data Cleaning**
2. **KPI Calculation**
3. **Visualization**
4. **Statistical Testing (A/B Test)**

---

## 📁 Project Structure
project-03/
│
├── data/
│ ├── Marketing_Campaign_Data.xlsx
│ └── campaigns_clean.csv
│
├── charts/
│ ├── chart1_ctr_by_platform.png
│ ├── chart2_roas_by_platform.png
│ ├── chart3_cac_by_platform.png
│ ├── chart4_monthly_spend.png
│ └── chart5_ab_test.png
│
├── scripts/
│ ├── clean.py
│ ├── 02_analyse.py
│ └── 03_stats_ab.py
│
└── README.md
---

## 📌 Key Metrics

### CTR (Click-Through Rate)
```math
### CTR = \frac{Clicks}{Impressions} \times 100

---
### CAC (Customer Acquisition Cost)
CAC=
Enrollments
Total Cost
---
```
---
### ROAS (Return on Ad Spend)
ROAS=
Cost
Revenue
---

---
### 2. 📊 Key Insights
🔹 Platform Performance
Platform	CTR (%)	ROAS (x)	CAC (₹)
Facebook	5.56	23.46	234
Google Ads	5.48	22.97	243
Instagram	5.46	24.01	230
LinkedIn	5.58	25.45	219
YouTube	    5.58	22.13	243

---

## Observations

LinkedIn → Best overall platform
Highest ROAS (25.45x)
Lowest CAC (₹219)
YouTube & Google Ads
Higher cost (₹243)
Lower efficiency → not ideal for scaling
CTR across platforms is very similar (~5.4–5.6%)
Suggests creative quality is consistent
Differences come from conversion efficiency, not clicks

---

## Monthly Spend Trend
Mostly stable: ₹30L–₹40L/month
Occasional spikes (~₹70L–₹80L)
Likely campaign bursts or launches

---

## A/B Testing
We compare top platforms using statistical testing.

Hypothesis:
H0: CTR is the same
H1: CTR is different

Using a t-test:

If p < 0.05 → significant difference
Else → difference is noise

```
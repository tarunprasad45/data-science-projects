# Retail Sales Analytics — Superstore Dataset
**Portfolio Project | Python · SQL (SQLite) · Pandas · Matplotlib · Scikit-learn**

---

## Overview

Full-stack retail analytics pipeline on the classic Superstore dataset (~10,000 order lines). The project goes beyond basic charting — it starts with proper database design, queries KPIs in SQL, produces six analytical charts, and ends with a regression-based revenue forecast. Structured to demonstrate skills relevant to a business analyst or data analyst role.

---

## Pipeline

| Script | What it does |
|---|---|
| `01_load_to_sql.py` | Normalises the flat CSV into 3 relational tables (`regions`, `products`, `orders`) in a SQLite database, then adds indexes for faster joins |
| `02_query_kpis.py` | Runs 5 SQL queries (with JOINs, GROUP BY, CASE-WHEN discount bucketing) to produce KPI tables saved as CSVs |
| `03_analyse.py` | Reads the KPI CSVs and generates 5 charts — including a dual-axis chart and a discount impact breakdown |
| `04_forecast.py` | Fits a Linear Regression model on 36 time periods and forecasts the next 6, with RMSE, R², and a 95% confidence interval |

---

## Why Normalise into a Database?

The raw file has strings like `"Office Supplies"` and `"West"` repeated on every row. Splitting into lookup tables (`regions`, `products`) and a fact table (`orders`) is standard relational database design — it reduces redundancy, enables faster GROUP BY queries at scale, and is the structure you'd see in any real retail data warehouse. Indexes were added on the foreign key columns to further speed up joins.

---

## Key Findings

### Revenue by Region
West leads at **$725K (14.9% margin)**, followed by East at $679K (13.5%). Central is the weakest performer — similar revenue to East but margin collapses to just **7.9%**, suggesting either a product mix or discount problem specific to that region.

### Revenue & Margin by Category
Technology generates the most revenue ($836K) and the highest margin at **17.4%**. Furniture is nearly as large in revenue ($742K) but margins are almost nonexistent at just **2.5%** — meaning it's contributing very little to actual profit despite being a major revenue line.

### Top Sub-Categories — Profitable vs Loss-Making
Of the top 10 sub-categories by revenue, **Tables (-$17,725)** and **Bookcases (-$3,473)** are actively loss-making despite generating hundreds of thousands in revenue. Phones and Chairs are the top earners in absolute profit terms. This is an actionable finding — these two sub-categories are subsidised by the rest of the business.

### Revenue by Customer Segment
Consumer segment drives **50.6% of total revenue** ($2.30M total). Corporate contributes 30.7% and Home Office 18.7%. The business is retail-skewed — there may be untapped margin opportunity in growing the Corporate segment, which typically demands less discounting.

### Discount Impact on Margin (Key Insight Chart)
This is the most commercially important chart in the project. Margin drops from **+29.5% with no discount** to **+11.9% at low discounts**, turns negative at mid-level discounts (-15.5%), and becomes catastrophically loss-making at high discounts (**-77.4%**). The business is destroying margin on a significant portion of its orders. Any pricing strategy review should start here.

### Revenue Forecast (Linear Regression)
Revenue was binned into 36 sequential periods and a linear model was fit to identify structural trend. R² = 0.001 indicates **no meaningful linear trend** — revenue is essentially flat and noisy rather than growing or declining. The low R² is itself the finding: it's reported honestly rather than hidden. The forecast of ~$63K/period reflects the mean with a wide 95% confidence interval, which accurately captures the high period-to-period variance. This demonstrates model evaluation literacy, not just model fitting.

---

## Skills Demonstrated

- **Database design** — denormalisation awareness, surrogate keys, indexed foreign keys in SQLite
- **SQL proficiency** — multi-table JOINs, GROUP BY aggregations, CASE-WHEN bucketing, ROUND and CAST for float division
- **Dual-axis visualisation** — twin y-axes to compare revenue ($) and margin (%) on the same chart without distortion
- **Business interpretation** — identifying loss-making sub-categories within profitable categories; framing discount impact as a pricing strategy issue
- **Regression forecasting** — Linear Regression with residual-based confidence intervals; honest R² reporting
- **Modular pipeline** — four independent scripts with clean data handoffs via CSV and SQLite

---

*Tools: Python 3, Pandas, Matplotlib, SQLite3, Scikit-learn*
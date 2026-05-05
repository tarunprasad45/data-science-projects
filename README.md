# 📊 Data Analytics Portfolio — Tarun Prasad

A collection of end-to-end data analytics projects demonstrating **SQL, Python, statistics, and machine learning**, with a strong focus on **business insight and structured pipelines**.

Each project follows a consistent approach:
> Clean data → Structure it → Analyse → Visualise → Derive insights → (Optional) Model

---

## 🚀 Projects

---

### 🎓 EdTech Lead Scoring Model
**Python · Pandas · Scikit-learn · Statsmodels · Imbalanced-learn**

🔗 [View Project](./EdTech_Lead_Scoring)

#### Overview
Lead scoring model for X Education, an online course platform converting only 38.3% of inbound leads. Built a full ML pipeline to assign every lead a 0–100 score and segment into Hot/Warm/Cold tiers — enabling sales teams to prioritise the highest-probability prospects instead of working the entire funnel uniformly.

#### Key Highlights
- Built 4-script pipeline: **clean → EDA → model → business insights**
- Model stack: **SMOTE + RFE (55→20 features) + iterative VIF pruning + threshold optimisation**
- Scaler deliberately fitted **post feature selection** to avoid column mismatch — documented explicitly
- Identified **near-perfect separation anomaly** in Occupation_Housewife coefficient rather than reporting it at face value

#### Key Insights
- **Hot tier (30% of leads) converts at 71.7%** vs 38.3% baseline — **1.9× lift**
- Working Professionals convert at **90.1%** vs Unemployed at 33.7% — acquisition audience mismatch
- Time on site median gap: **1,047s (converters) vs 260s (non-converters)** — 4× behavioural signal
- Referral Sites convert at **61.1%** vs Direct Traffic at 32.6% — paid search producing lowest-quality leads
- AUC **0.753**, Accuracy **74.1%**, Specificity **85.0%** on held-out test set

---

### 🏦 Indian Banking Sector Analysis  
**Python · Pandas · Matplotlib · Financial Analysis**

🔗 [View Project](./Indian_Banking_Sector)

#### Overview
End-to-end analysis of the Indian banking system using RBI data (~25 years). Focused on understanding the relationship between **credit growth, deposit dynamics, and asset quality (NPAs)** across economic cycles.

#### Key Highlights
- Built a robust data pipeline to clean and structure **messy RBI datasets with multi-level headers**
- Aggregated bank-level NPA data into **system-level risk indicators (correctly recomputed percentages)**
- Engineered key financial metrics: **credit growth, deposit growth, GNPA %, NNPA %, and credit-deposit ratio**
- Developed time-series visualizations to identify **structural shifts in banking cycles**

#### Key Insights
- Banking sector moved through **clear cycles**: cleanup (1996–2008), risk buildup (post-2008), AQR-driven stress (2015–18), and recovery (post-2020)
- GNPA declined from ~15% → ~2%, then spiked >10% before falling again — highlighting **risk recognition vs risk creation**
- Credit growth remains strong while NPAs decline → **healthier lending environment**
- Credit-to-Deposit ratio increased from ~0.55 → ~0.80, signalling **tightening liquidity conditions**

---

### 🛒 Retail Sales Analytics  
**Python · SQL (SQLite) · Pandas · Matplotlib · Scikit-learn**

🔗 [View Project](./Retail_Sales_Analytics)

#### Overview
Full-stack retail analytics pipeline built on the Superstore dataset (~10K rows). Combines **database design, SQL analytics, visualisation, and forecasting**.

#### Key Highlights
- Designed **relational database (3 tables + indexing)** instead of flat analysis  
- Wrote SQL queries with **JOIN, GROUP BY, CASE-WHEN**  
- Built **dual-axis business charts (Revenue vs Margin)**  
- Implemented **Linear Regression forecast with confidence intervals**

#### Key Insights
- Discounts destroy margins: **+29% → -77% at high discount levels**
- Furniture generates revenue but almost **no profit (2.5% margin)**
- No real revenue trend → **R² ≈ 0 (honest modelling insight)**

---

### 📢 Marketing Campaign Analysis  
**Python · Pandas · Matplotlib · SciPy**

🔗 [View Project](./Marketing_Campaign_Analysis)

#### Overview
Multi-platform marketing analysis (Jan 2024 – Oct 2025) with **KPI design + statistical testing**.

#### Key Highlights
- Built full pipeline: **clean → analyse → statistical testing**
- Designed core metrics: **CTR, ROAS, CAC**
- Ran **A/B hypothesis testing (Z-test)**

#### Key Insights
- All platforms perform similarly → **CTR ~5.5% across channels**
- LinkedIn surprisingly best: **25x ROAS, lowest CAC**
- A/B test result: **No significant difference (p = 0.73)**

---

### 🧑‍💻 E-Commerce Customer Analysis  
**Python · Pandas · Matplotlib · Scikit-learn**

🔗 [View Project](./Ecommerce_Customer_analysis)

#### Overview
Customer behaviour analysis + segmentation using **unsupervised learning (KMeans)**.

#### Key Highlights
- Analysed **spending behaviour, satisfaction, discount effects**
- Applied **feature scaling + clustering**
- Translated clusters into **business-friendly segments**

#### Key Insights
- Gold customers spend **~3× more than Bronze**
- Only **35% customers satisfied → retention risk**
- Identified 3 segments: High Value, Occasional, At Risk

---

## 🧠 Skills Demonstrated

### 📊 Data Analysis
- Exploratory Data Analysis (EDA)
- KPI Design (CTR, ROAS, CAC, Margin, Conversion Rate, Lead Score)
- Business Insight Extraction
- Funnel & Conversion Analysis

### 🗄️ Data Engineering
- Relational Database Design
- SQL (JOIN, GROUP BY, CASE WHEN)
- Data Pipelines
- Feature Engineering & Category Consolidation

### 📈 Visualisation
- Matplotlib (bar, line, scatter, dual-axis, histogram, donut)
- Insight-driven charting (not just plotting)
- KPI Dashboard Cards

### 🤖 Machine Learning
- Logistic Regression (lead scoring + threshold optimisation)
- Linear Regression (forecasting + evaluation)
- KMeans Clustering (customer segmentation)
- SMOTE (class imbalance handling)
- RFE (feature selection)
- Feature Scaling & Model Interpretation

### 📐 Statistics
- Hypothesis Testing (Z-test / t-test)
- p-value interpretation
- Confidence Intervals
- VIF (multicollinearity detection)
- ROC / AUC analysis

---

## ⚙️ Tech Stack

- Python (Pandas, NumPy, Matplotlib, Scikit-learn, Statsmodels, Imbalanced-learn, SciPy)
- SQL (SQLite)
- Excel (raw data handling)

---

## 📌 What Makes This Portfolio Different?

- Not just charts — **structured pipelines**
- Not just models — **business interpretation**
- Not just results — **honest evaluation**
- Focus on **real-world decision-making, not textbook outputs**
- Hypotheses formed **before** analysis — confirmed or rejected with data

---
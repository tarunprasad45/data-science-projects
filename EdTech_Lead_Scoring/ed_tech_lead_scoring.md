# EdTech Lead Scoring Model
**Portfolio Project | Python · Pandas · Scikit-learn · Statsmodels · Imbalanced-learn**

---

## Overview

X Education sells online courses and generates thousands of inbound leads — but converts only **38.3%** of them. The remaining 61.7% represent wasted acquisition spend and sales effort spread too thin across unqualified prospects.

This project builds a **logistic regression lead scoring model** that assigns every lead a 0–100 score and buckets them into Hot, Warm, and Cold tiers — so the sales team can concentrate effort on the highest-probability leads instead of working the entire funnel uniformly.

**Dataset:** 9,240 leads, 37 features — lead source, website engagement (time on site, page views, visits), occupation, geography, last activity, and marketing touchpoints.  
**Source:** [X Education Lead Scoring Dataset — Kaggle](https://www.kaggle.com/datasets/amritachatterjee09/predictive-lead-data-for-edtech)

---

## Pipeline

| Script | What it does |
|---|---|
| `01_clean.py` | Replaces 'Select' placeholders with NaN; drops 8 columns exceeding 30% missingness; mode/median/geography-aware imputation; consolidates 15+ noisy Lead Source categories into 7; groups 80+ countries into 6 macro-regions |
| `02_eda.py` | Conversion rate by lead source, last activity, occupation; time-on-site distribution split by conversion outcome; identifies the 4 key behavioural signals that separate converters |
| `03_model.py` | Full model pipeline: encode → float cast → train/test split → SMOTE → RFE (55→20 features) → iterative GLM with VIF pruning → scaler fitted post-feature-selection → threshold optimisation → test set evaluation |
| `04_insights.py` | Scores all 7,123 leads; generates tier distribution vs actual conversion; score separation histogram; KPI summary card |

---

## Key EDA Findings

### Lead Source — 1.9x conversion gap across channels
Referral Sites convert at **61.1%** while Direct Traffic converts at only **32.6%** — nearly a 2x difference across the same funnel. Search Engines dominate volume (n=4,016) but convert at just 39.6%. This means the majority of acquisition spend (paid search) is producing the second-lowest quality leads.

### Last Activity — the strongest real-time signal
Last activity is the clearest leading indicator of conversion intent. Leads whose last recorded activity was a phone conversation convert at **73.3%**; SMS Sent follows at 57.5%. At the bottom, Email Bounced (9.1%) and Converted to Lead (13.1%) are effectively cold. The CRM activity log is a near-real-time quality signal that isn't being systematically used for prioritisation.

### Time on Site — 4x median gap between converters and non-converters
Converting leads spend a **median of 1,047 seconds** on site vs 260 seconds for non-converters — a 4x difference. The distribution overlap is minimal above 750 seconds; a time-on-site threshold alone would capture a large fraction of eventual converters, making it one of the strongest single features in the model.

### Occupation — volume vs quality inversion
Unemployed leads make up **89.6% of all leads** (n=6,383) but convert at only 33.7%. Working Professionals are a tiny fraction (n=543) but convert at **90.1%**. The platform's top-of-funnel content is attracting the wrong audience relative to its highest-converting segment — a significant acquisition efficiency problem.

---

## Model

### Architecture
Logistic Regression with the following pipeline:

1. **One-hot encoding** of all categorical variables (drop-first to avoid perfect collinearity)
2. **SMOTE** on training set only — synthetic minority oversampling to address the 62/38 class split without touching the test set
3. **RFE** (Recursive Feature Elimination) — 55 encoded features → 20 selected by cross-validated importance
4. **Iterative VIF pruning** — 4 rounds of statsmodels GLM fitting, dropping the highest-VIF collinear feature each round until all VIF < 5
5. **StandardScaler** fitted only on numeric columns that survived into the final feature set (fitting before feature selection causes column mismatch errors)
6. **Threshold optimisation** — sensitivity/specificity crossover at 0.475 selected over the arbitrary default of 0.5

### Why Logistic Regression over tree models?
Logistic regression produces **calibrated probabilities** — the 0–100 score is monotonic and interpretable. A sales team using this score to prioritise calls needs to understand *why* a lead is scored high, not just that it is. The GLM coefficients directly answer that question.

### Why SMOTE on train only?
Applying SMOTE to the full dataset before splitting would leak synthetic samples into the test set, producing artificially inflated metrics. SMOTE is applied exclusively to the training split — the test set retains the original class distribution for honest evaluation.

### Why VIF iteration instead of just RFE?
RFE selects features by importance but doesn't remove correlated features that survive together. Correlated features inflate each other's apparent importance and produce unstable coefficients. The VIF iteration (statsmodels GLM with exact p-values) removes multicollinearity scientifically rather than arbitrarily.

---

## Results

### Test Set Metrics

| Metric | Value |
|---|---|
| Accuracy | **74.1%** |
| AUC Score | **75.3%** |
| Sensitivity (Recall) | **56.9%** |
| Specificity | **85.0%** |
| Optimal Threshold | **0.475** |
| Test Set Size | 1,781 leads |

The AUC of 0.753 means the model correctly ranks a randomly chosen converter above a randomly chosen non-converter 75.3% of the time — a meaningful improvement over random (0.5). Specificity of 85% is deliberately prioritised: it's more expensive to waste a sales call on a cold lead than to miss one warm lead.

Sensitivity of 56.9% is intentionally below specificity — this reflects the threshold choice. At 0.475, we accept missing some real converters to avoid flooding the sales team with false positives.

### Lead Tier Business Impact

| Tier | Score | Leads | Actual Conversion |
|---|---|---|---|
| **Hot** | 65–100 | 2,125 (29.8%) | **71.7%** |
| **Warm** | 40–65 | 780 (11.0%) | 29.4% |
| **Cold** | 0–40 | 4,216 (59.2%) | 23.1% |

**Conversion lift on Hot tier: 1.9×** vs the 38.3% baseline.

A sales team that focuses exclusively on Hot leads works 30% of the lead volume and sees 71.7% conversion — nearly double the baseline rate. The Cold tier (59% of leads) converts at 23.1%, below baseline, confirming these leads should receive only automated drip communication rather than direct sales effort.

### Feature Importance
The top conversion-positive signals from the GLM coefficients:
- **Occupation: Working Professional** — strongest legitimate predictor; high intent, high ability to pay
- **Lead Source: Welingak Website** — proprietary channel, pre-qualified audience
- **Last Activity: SMS Sent** — active engagement signal, recent touchpoint
- **Lead Origin: Lead Add Form** — self-initiated, high intent

Note: `Occupation_Housewife` appears with an extremely large coefficient (~30,000) due to a near-perfect separation issue with that category on a small sample — a known logistic regression edge case with rare categories. This should be treated with caution and monitored in production.

---

## Skills Demonstrated

- **Feature engineering** — geographic macro-region grouping, 'Select' placeholder treatment, category consolidation
- **Class imbalance handling** — SMOTE applied correctly (train set only, test set untouched)
- **Statistical modelling** — statsmodels GLM with p-value inspection and VIF iteration; not sklearn black-box
- **Pipeline ordering** — scaler fitted after feature selection to avoid column mismatch; documented explicitly
- **Model evaluation literacy** — threshold optimisation with explicit sensitivity/specificity tradeoff; honest AUC and sensitivity reporting
- **Business translation** — model scores → Hot/Warm/Cold tiers → sales prioritisation framework with quantified lift
- **Anomaly flagging** — identified the near-perfect separation issue with Occupation_Housewife rather than reporting the coefficient at face value

---

## How to Run

```bash
# Install dependencies
pip install pandas numpy matplotlib scikit-learn imbalanced-learn statsmodels

# Download dataset from Kaggle and place as:
# data/Leads.csv

# Run pipeline in order
python scripts/01_clean.py
python scripts/02_eda.py
python scripts/03_model.py
python scripts/04_insights.py
```

Charts save to `charts/`, KPI tables to `data/`.

---

*Tools: Python 3, Pandas, NumPy, Matplotlib, Scikit-learn, Imbalanced-learn, Statsmodels*  
*Dataset: X Education Leads — [Kaggle](https://www.kaggle.com/datasets/amritachatterjee09/predictive-lead-data-for-edtech)*
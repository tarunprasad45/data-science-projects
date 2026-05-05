"""
01_clean.py
-----------
Loads the raw X Education leads dataset (Leads.csv), cleans it,
and saves a clean version for all downstream analysis.

Dataset: 9,240 leads, ~37 columns
Source  : https://www.kaggle.com/datasets/amritachatterjee09/predictive-lead-data-for-edtech

What this script does:
  1. Rename verbose column names to concise aliases
  2. Replace 'Select' placeholder values with NaN (unfilled optional fields)
  3. Drop columns with >30% missing values (industry standard threshold)
  4. Drop non-predictive ID columns
  5. Impute categoricals: mode for Lead Source/Last Activity,
     geography-aware fill for Country → Region grouping,
     majority-class fill for Occupation and Goal
  6. Impute numericals: median for TotalVisits and Pages Viewed
     (median chosen because both are right-skewed with outliers)
  7. Consolidate noisy low-frequency categories in Lead Source,
     Last Activity, Last Notable Activity
  8. Group Country into 6 macro-regions, rename to Region
  9. Save to data/leads_clean.csv

Why median imputation for numeric columns?
  TotalVisits and Pages Viewed have extreme right tails
  (p99 >> p75). Mean imputation would inflate values for missing rows.
  Median is resistant to outliers and more representative of the
  typical lead's behaviour.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "data", "Leads.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "leads_clean.csv")

# ── Step 1: Load ──────────────────────────────────────────────────────────────
print("Loading raw data...")
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df):,} rows × {len(df.columns)} columns.")

df_backup = df.copy()

# ── Step 2: Rename columns ────────────────────────────────────────────────────
df = df.rename(columns={
    'Page Views Per Visit'                        : 'Pages Viewed',
    'Total Time Spent on Website'                 : 'Time on Site',
    'What is your current occupation'             : 'Occupation',
    'How did you hear about X Education'          : 'Discoveredby',
    'What matters most to you in choosing a course': 'Goal',
    'Search'                                      : 'Search_ad',
    'Magazine'                                    : 'Magazine_ad',
    'Newspaper Article'                           : 'Article_ad',
    'X Education Forums'                          : 'Forum_ad',
    'Newspaper'                                   : 'Newspaper_ad',
    'Digital Advertisement'                       : 'Dig_ad',
    'Through Recommendations'                     : 'Recommendation',
    'Receive More Updates About Our Courses'      : 'Updates',
    'Update me on Supply Chain Content'           : 'Supply Chain',
    'Get updates on DM Content'                   : 'DM',
    'Asymmetrique Activity Index'                 : 'Activity Index',
    'Asymmetrique Profile Index'                  : 'Profile Index',
    'Asymmetrique Activity Score'                 : 'Activity Score',
    'Asymmetrique Profile Score'                  : 'Profile Score',
    'I agree to pay the amount through cheque'    : 'Pay by Cheque',
    'A free copy of Mastering The Interview'      : 'Free copy',
})
print("Columns renamed.")

# ── Step 3: Replace 'Select' with NaN ────────────────────────────────────────
df.replace('Select', np.nan, inplace=True)
print("'Select' placeholders replaced with NaN.")

# ── Step 4: Drop high-missingness columns (>30%) ─────────────────────────────
missing_pct = df.isnull().sum() / len(df) * 100
cols_to_drop = missing_pct[missing_pct > 30].index.tolist()
print(f"\nDropping {len(cols_to_drop)} columns with >30% missing: {cols_to_drop}")
df.drop(columns=cols_to_drop, inplace=True)

# Drop ID columns — no predictive value
df.drop(columns=['Prospect ID', 'Lead Number'], inplace=True, errors='ignore')

# ── Step 5: Impute categoricals ───────────────────────────────────────────────
# 5a. Mode imputation for Lead Source and Last Activity
for col in ['Last Activity', 'Lead Source']:
    if col in df.columns:
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)
        print(f"  Imputed '{col}' with mode: '{mode_val}'")

# 5b. Country → geography-aware → India (dominant class: ~70%)
df['Country'] = df['Country'].fillna('India')

# 5c. Occupation → Unemployed (dominant class: ~60%)
if 'Occupation' in df.columns:
    df['Occupation'] = df['Occupation'].fillna('Unemployed')

# 5d. Goal → mode
if 'Goal' in df.columns:
    df['Goal'] = df['Goal'].fillna(df['Goal'].mode()[0])

# ── Step 6: Impute numericals with median ────────────────────────────────────
for col in ['TotalVisits', 'Pages Viewed']:
    if col in df.columns:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"  Imputed '{col}' with median: {median_val}")

missing_remaining = df.isnull().sum().sum()
print(f"\nTotal remaining missing values: {missing_remaining}")

# ── Step 7: Consolidate noisy Lead Source categories ─────────────────────────
if 'Lead Source' in df.columns:
    df['Lead Source'] = df['Lead Source'].replace({
        'google': 'Search Engines', 'Google': 'Search Engines',
        'bing': 'Search Engines',   'Organic Search': 'Search Engines',
        'Olark Chat': 'Live Chat',
        'Reference': 'Referral Sites',
        'Facebook': 'Social Media',  'youtubechannel': 'Social Media',
        'welearnblog_Home': 'Welingak Website',
        'WeLearn': 'Welingak Website', 'blog': 'Welingak Website',
    })
    other_sources = ['Pay per Click Ads', 'Click2call', 'Press_Release', 'NC_EDM', 'testone']
    df['Lead Source'] = df['Lead Source'].replace({s: 'Other Sources' for s in other_sources})

# Consolidate Last Activity rare categories
if 'Last Activity' in df.columns:
    rare_activities = [
        'Approached upfront', 'View in browser link Clicked',
        'Email Received', 'Email Marked Spam',
        'Visited Booth in Tradeshow', 'Resubscribed to emails'
    ]
    df['Last Activity'] = df['Last Activity'].replace({a: 'Others' for a in rare_activities})

# Consolidate Last Notable Activity (< 15 occurrences → Others)
if 'Last Notable Activity' in df.columns:
    rare_notable = df['Last Notable Activity'].value_counts()
    rare_notable = rare_notable[rare_notable < 15].index
    df['Last Notable Activity'] = df['Last Notable Activity'].replace(
        {a: 'Others' for a in rare_notable}
    )

# ── Step 8: Group Country into macro-regions, rename column ──────────────────
region_map = {
    'Asia'       : ['India', 'Singapore', 'Hong Kong', 'Philippines', 'Asia/Pacific Region',
                    'Bangladesh', 'China', 'Sri Lanka', 'Malaysia', 'Vietnam', 'Indonesia'],
    'America'    : ['United States', 'Canada'],
    'Middle_East': ['United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Bahrain', 'Oman', 'Kuwait'],
    'Europe'     : ['United Kingdom', 'France', 'Germany', 'Sweden', 'Italy', 'Netherlands',
                    'Belgium', 'Switzerland', 'Denmark', 'Russia'],
    'Australia'  : ['Australia'],
    'Africa'     : ['South Africa', 'Nigeria', 'Uganda', 'Ghana', 'Kenya', 'Tanzania', 'Liberia'],
}
country_to_region = {country: region for region, countries in region_map.items()
                     for country in countries}
df['Country'] = df['Country'].map(country_to_region).fillna('Other')
df.rename(columns={'Country': 'Region'}, inplace=True)

# ── Step 9: Check duplicates ──────────────────────────────────────────────────
dupes = df.duplicated().sum()
print(f"Duplicate rows: {dupes}")
if dupes > 0:
    df = df.drop_duplicates()

# ── Step 10: Save ─────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nClean data saved → {OUTPUT_FILE}")
print(f"Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ── Quick conversion summary ──────────────────────────────────────────────────
if 'Converted' in df.columns:
    conv_rate = df['Converted'].astype(int).mean() * 100
    print(f"\nOverall conversion rate: {conv_rate:.1f}%")
    print(f"Converted leads  : {df['Converted'].astype(int).sum():,}")
    print(f"Non-converted    : {(~df['Converted'].astype(bool)).sum():,}")
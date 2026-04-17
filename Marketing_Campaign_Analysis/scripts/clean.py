"""
clean.py
--------
Loads the raw campaign data, does basic cleaning,
and saves a clean CSV for analysis.

What it does:
- Loads the CampaignPerformance sheet from the Excel file
- Renames columns to simpler names (no spaces, no symbols)
- Checks for missing values and duplicate rows
- Saves a clean version to data/campaigns_clean.csv
"""

import pandas as pd
import os

# --- File paths ---
# os.path.dirname(__file__) gives us the scripts/ folder
# Going one level up (..) gives us the project root (project-01/)
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "data", "Marketing_Campaign_Data.xlsx")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "campaigns_clean.csv")

# --- Step 1: Load the data ---
print("Loading data...")
df = pd.read_excel(INPUT_FILE, sheet_name="CampaignPerformance")
print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

# --- Step 2: Rename columns ---
# Remove spaces and the ₹ symbol so columns are easy to work with in code
df = df.rename(columns={
    "Date"           : "date",
    "CampaignID"     : "campaign_id",
    "CampaignName"   : "campaign_name",
    "Platform"       : "platform",
    "TargetAudience" : "target_audience",
    "Impressions"    : "impressions",
    "Clicks"         : "clicks",
    "Leads"          : "leads",
    "Applications"   : "applications",
    "Enrollments"    : "enrollments",
    "Cost (₹)"       : "cost",
    "Revenue (₹)"    : "revenue",
    "Region"         : "region",
})

print("Columns renamed.")

# --- Step 3: Check for missing values ---
missing = df.isnull().sum().sum()
if missing == 0:
    print("No missing values found. Good to go!")
else:
    print(f"Found {missing} missing values. Dropping those rows.")
    df = df.dropna()

# --- Step 4: Check for duplicate rows ---
duplicates = df.duplicated().sum()
if duplicates == 0:
    print("No duplicate rows found.")
else:
    print(f"Found {duplicates} duplicate rows. Removing them.")
    df = df.drop_duplicates()

# --- Step 5: Make sure date column is the right type ---
df["date"] = pd.to_datetime(df["date"])

# --- Step 6: Save clean data ---
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nClean data saved to: {OUTPUT_FILE}")
print(f"Final shape: {df.shape[0]} rows, {df.shape[1]} columns")

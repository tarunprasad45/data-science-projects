"""
clean.py
--------
Loads the raw customer behaviour data, cleans it,
and saves a clean version for analysis.

What it does:
- Renames columns to simpler names (no spaces)
- Handles 2 missing values in Satisfaction Level
- Converts True/False to Yes/No for readability
- Saves clean data to data/customers_clean.csv
"""

import pandas as pd
import os

# --- File paths ---
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "data", "E-commerce Customer Behavior - Sheet1.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "customers_clean.csv")

# --- Step 1: Load ---
print("Loading data...")
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

# --- Step 2: Rename columns ---
df = df.rename(columns={
    "Customer ID"             : "customer_id",
    "Gender"                  : "gender",
    "Age"                     : "age",
    "City"                    : "city",
    "Membership Type"         : "membership_type",
    "Total Spend"             : "total_spend",
    "Items Purchased"         : "items_purchased",
    "Average Rating"          : "avg_rating",
    "Discount Applied"        : "discount_applied",
    "Days Since Last Purchase": "days_since_purchase",
    "Satisfaction Level"      : "satisfaction",
})
print("Columns renamed.")

# --- Step 3: Handle missing values ---
missing = df.isnull().sum().sum()
print(f"\nMissing values found: {missing}")

# Only 2 nulls in satisfaction — fill with 'Unknown' instead of dropping rows
df["satisfaction"] = df["satisfaction"].fillna("Unknown")
print("Filled missing satisfaction values with 'Unknown'.")

# --- Step 4: Convert discount column to readable Yes/No ---
df["discount_applied"] = df["discount_applied"].map({True: "Yes", False: "No"})

# --- Step 5: Check for duplicates ---
dupes = df.duplicated().sum()
if dupes == 0:
    print("No duplicate rows found.")
else:
    print(f"{dupes} duplicates found. Removing.")
    df = df.drop_duplicates()

# --- Step 6: Save ---
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nClean data saved to: {OUTPUT_FILE}")
print(f"Final shape: {df.shape[0]} rows, {df.shape[1]} columns")
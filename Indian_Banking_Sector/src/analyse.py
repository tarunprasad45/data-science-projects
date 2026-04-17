import pandas as pd
import os

# -------------------------------
# PATHS
# -------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------------
# LOAD DATA
# -------------------------------

def load_data():
    assets = pd.read_csv(os.path.join(PROCESSED_DIR, "assets_liabilities_clean.csv"))
    npa = pd.read_csv(os.path.join(PROCESSED_DIR, "npa_clean.csv"))
    return assets, npa


# -------------------------------
# FORCE NUMERIC (CRITICAL)
# -------------------------------

def force_numeric(df, cols):
    for col in cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("-", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# -------------------------------
# AGGREGATE NPA (FIX DUPLICATES)
# -------------------------------

def aggregate_npa(npa):

    # Clean numeric columns first
    cols = ["gross_advances", "gnpa_amount", "nnpa_amount"]

    for col in cols:
        npa[col] = (
            npa[col]
            .astype(str)
            .str.replace(",", "", regex=False)
        )
        npa[col] = pd.to_numeric(npa[col], errors="coerce")

    # Aggregate to ONE ROW PER YEAR
    grouped = npa.groupby("year").agg({
        "gross_advances": "sum",
        "gnpa_amount": "sum",
        "nnpa_amount": "sum"
    }).reset_index()

    # Recalculate percentages (VERY IMPORTANT)
    grouped["gnpa_pct"] = (grouped["gnpa_amount"] / grouped["gross_advances"]) * 100
    grouped["nnpa_pct"] = (grouped["nnpa_amount"] / grouped["gross_advances"]) * 100

    return grouped


# -------------------------------
# BUILD CORE DATASET
# -------------------------------

def build_core_dataset(assets, npa):

    # Select relevant columns
    df = assets[[
        "year",
        "aggregate_deposits_2+3",
        "bank_credit_11+12"
    ]].copy()

    # Rename for clarity
    df.rename(columns={
        "aggregate_deposits_2+3": "deposits",
        "bank_credit_11+12": "credit"
    }, inplace=True)

    # Clean year
    df["year"] = df["year"].astype(str).str.strip()
    npa["year"] = npa["year"].astype(str).str.strip()

    # Merge
    df = pd.merge(df, npa, on="year", how="inner")

    # Convert to numeric
    numeric_cols = [
        "credit",
        "deposits",
        "gnpa_amount",
        "gnpa_pct",
        "nnpa_amount",
        "nnpa_pct"
    ]

    df = force_numeric(df, numeric_cols)

    # Drop bad rows
    df.dropna(subset=["credit", "deposits"], inplace=True)

    # Sort
    df = df.sort_values("year")

    # -------------------------------
    # FEATURE ENGINEERING
    # -------------------------------

    df["credit_growth"] = df["credit"].pct_change() * 100
    df["deposit_growth"] = df["deposits"].pct_change() * 100
    df["cd_ratio"] = df["credit"] / df["deposits"]

    return df


# -------------------------------
# SAVE OUTPUT
# -------------------------------

def save_output(df):
    path = os.path.join(OUTPUT_DIR, "core_dataset.csv")
    df.to_csv(path, index=False)
    print("✅ Core dataset saved at:", path)


# -------------------------------
# MAIN
# -------------------------------

def main():
    assets, npa = load_data()

    # 🔥 Fix duplicates before merge
    npa = aggregate_npa(npa)

    df = build_core_dataset(assets, npa)

    print("\n📊 Preview:")
    print(df.tail())

    save_output(df)


if __name__ == "__main__":
    main()


    
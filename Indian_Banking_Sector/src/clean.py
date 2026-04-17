import pandas as pd
import os

# -------------------------------
# PATH SETUP (ROBUST)
# -------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)


# -------------------------------
# HELPERS
# -------------------------------

def clean_column_names(df):
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[()%-]", "", regex=True)
    )
    return df


def convert_numeric(df):
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("₹", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df


# -------------------------------
# CLEAN: ASSETS & LIABILITIES
# -------------------------------

def clean_assets_liabilities():
    print("Cleaning assets & liabilities...")

    file_path = os.path.join(RAW_DIR, "assets_liabilities.csv")

    # Step 1: read raw
    df_raw = pd.read_csv(file_path, header=None)

    # Step 2: find header row (where 'Year' appears)
    header_idx = df_raw[df_raw[0].astype(str).str.contains("Year", na=False)].index[0]

    # Step 3: reload with correct header
    df = pd.read_csv(file_path, skiprows=header_idx)

    # Step 4: drop numbering row (1,2,3...)
    df = df[df.iloc[:, 0].astype(str).str.strip() != "1"]

    # Step 5: clean
    df = clean_column_names(df)
    df = convert_numeric(df)

    df.dropna(how="all", inplace=True)

    # clean year column
    if "year" in df.columns:
        df["year"] = df["year"].astype(str).str.strip()

    df = df.sort_values(by=df.columns[0])

    output_path = os.path.join(PROCESSED_DIR, "assets_liabilities_clean.csv")
    df.to_csv(output_path, index=False)

    print("✅ assets_liabilities cleaned")

# -------------------------------
# CLEAN: NPA DATA
# -------------------------------

def clean_npa():
    print("Cleaning NPA data...")

    file_path = os.path.join(RAW_DIR, "gnpa_nnpa.csv")

    # Read raw
    df_raw = pd.read_csv(file_path, header=None)

    # Find header row (contains 'Year')
    header_idx = df_raw[df_raw[0].astype(str).str.contains("Year", na=False)].index[0]

    # Read from that row
    df = pd.read_csv(file_path, skiprows=header_idx)

    # Drop useless header rows
    df = df[df.iloc[:, 0].astype(str).str.contains(r"\d{4}-\d{2}", na=False)]

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # Manually assign clean column names (VERY IMPORTANT)
    df.columns = [
        "year",
        "gross_advances",
        "net_advances",
        "gnpa_amount",
        "gnpa_pct",
        "gnpa_pct_assets",
        "nnpa_amount",
        "nnpa_pct",
        "nnpa_pct_assets",
        "extra"
    ]

    # Drop extra column
    df = df.drop(columns=["extra"])

    # Clean values
    df = convert_numeric(df)

    # Clean year
    df["year"] = df["year"].astype(str).str.strip()

    # Sort
    df = df.sort_values("year")

    # Save
    output_path = os.path.join(PROCESSED_DIR, "npa_clean.csv")
    df.to_csv(output_path, index=False)

    print("✅ npa cleaned PROPERLY")
    
# -------------------------------
# MAIN
# -------------------------------

def main():
    clean_assets_liabilities()
    clean_npa()


if __name__ == "__main__":
    main()
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------------
# PATHS
# -------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHART_DIR = os.path.join(OUTPUT_DIR, "charts")

os.makedirs(CHART_DIR, exist_ok=True)


# -------------------------------
# LOAD DATA
# -------------------------------

def load_data():
    return pd.read_csv(os.path.join(OUTPUT_DIR, "core_dataset.csv"))


# -------------------------------
# CHART 1: CREDIT VS DEPOSIT GROWTH
# -------------------------------

def plot_growth(df):
    plt.figure()

    plt.plot(df["year"], df["credit_growth"], label="Credit Growth")
    plt.plot(df["year"], df["deposit_growth"], label="Deposit Growth")

    plt.xticks(rotation=45)
    plt.title("Credit vs Deposit Growth")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "growth.png"))
    plt.close()


# -------------------------------
# CHART 2: NPA TREND
# -------------------------------

def plot_npa(df):
    plt.figure()

    plt.plot(df["year"], df["gnpa_pct"], label="GNPA %")
    plt.plot(df["year"], df["nnpa_pct"], label="NNPA %")

    plt.xticks(rotation=45)
    plt.title("NPA Trend")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "npa.png"))
    plt.close()


# -------------------------------
# CHART 3: CD RATIO
# -------------------------------

def plot_cd_ratio(df):
    plt.figure()

    plt.plot(df["year"], df["cd_ratio"])

    plt.xticks(rotation=45)
    plt.title("Credit / Deposit Ratio")

    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "cd_ratio.png"))
    plt.close()


# -------------------------------
# MAIN
# -------------------------------

def main():
    df = load_data()

    plot_growth(df)
    plot_npa(df)
    plot_cd_ratio(df)

    print("✅ Charts saved in output/charts/")


if __name__ == "__main__":
    main()


    
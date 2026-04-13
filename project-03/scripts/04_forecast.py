"""
04_forecast.py
--------------
Builds a revenue forecast using Linear Regression.

Since the Superstore dataset has no date column, we use order_line_id
as a sequential time proxy — each batch of ~277 rows ≈ one "period".
We create 36 equal-sized periods and forecast the next 6.

What this script does:
  1. Pulls all orders from SQLite
  2. Bins them into 36 time periods (by order_line_id rank)
  3. Fits a LinearRegression on periods 1–36
  4. Forecasts periods 37–42
  5. Computes RMSE and R² to evaluate the model
  6. Saves chart6_forecast.png

Why linear regression?
  It's the right starting point for trend forecasting — simple,
  interpretable, and shows whether revenue has an upward/downward
  structural trend. Interviewers love seeing you explain *why* you
  picked a model, not just that you used one.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH    = os.path.join(BASE_DIR, "data", "retail.db")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
DATA_DIR   = os.path.join(BASE_DIR, "data")
os.makedirs(CHARTS_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.dpi"      : 150,
    "font.family"     : "DejaVu Sans",
    "axes.spines.top" : False,
    "axes.spines.right": False,
    "axes.grid"       : True,
    "grid.alpha"      : 0.25,
    "axes.titlesize"  : 13,
    "axes.titleweight": "bold",
    "axes.labelsize"  : 10,
})

# ── Pull orders from DB ───────────────────────────────────────────────────────
print("Loading orders from retail.db...")
conn = sqlite3.connect(DB_PATH)
orders = pd.read_sql_query("SELECT order_line_id, sales FROM orders ORDER BY order_line_id", conn)
conn.close()
print(f"  {len(orders):,} order lines loaded.\n")

# ── Create time periods ───────────────────────────────────────────────────────
N_PERIODS  = 36
FORECAST_N = 6

orders["period"] = pd.cut(
    orders["order_line_id"],
    bins=N_PERIODS,
    labels=range(1, N_PERIODS + 1)
).astype(int)

period_revenue = orders.groupby("period")["sales"].sum().reset_index()
period_revenue.columns = ["period", "revenue"]

print("Revenue per period (sample):")
print(period_revenue.head(8).to_string(index=False))
print(f"  ...{N_PERIODS} periods total\n")

# ── Fit Linear Regression ─────────────────────────────────────────────────────
X_train = period_revenue[["period"]].values
y_train = period_revenue["revenue"].values

model = LinearRegression()
model.fit(X_train, y_train)
y_pred_train = model.predict(X_train)

# ── Evaluate ──────────────────────────────────────────────────────────────────
rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
r2   = r2_score(y_train, y_pred_train)

print("=" * 50)
print("MODEL EVALUATION")
print("=" * 50)
print(f"  Intercept  : {model.intercept_:,.2f}")
print(f"  Slope      : {model.coef_[0]:,.2f}  (revenue change per period)")
print(f"  R²         : {r2:.4f}  (1.0 = perfect fit)")
print(f"  RMSE       : ${rmse:,.2f}")
print()

slope_dir = "upward" if model.coef_[0] > 0 else "downward"
print(f"  Trend: {slope_dir} — revenue {'growing' if slope_dir == 'upward' else 'declining'} by"
      f" ${abs(model.coef_[0]):,.0f} per period on average.\n")

# ── Forecast next 6 periods ───────────────────────────────────────────────────
future_periods = np.arange(N_PERIODS + 1, N_PERIODS + FORECAST_N + 1).reshape(-1, 1)
forecast       = model.predict(future_periods)

# Confidence interval (±1.96 * residual std = ~95% band)
residual_std = np.std(y_train - y_pred_train)
ci_upper = forecast + 1.96 * residual_std
ci_lower = forecast - 1.96 * residual_std

forecast_df = pd.DataFrame({
    "period"   : future_periods.flatten(),
    "forecast" : forecast.round(2),
    "ci_lower" : ci_lower.round(2),
    "ci_upper" : ci_upper.round(2),
})

print("Forecast (next 6 periods):")
print(forecast_df.to_string(index=False))

forecast_df.to_csv(os.path.join(DATA_DIR, "forecast.csv"), index=False)
print("\n  Saved → data/forecast.csv\n")

# ── Chart ─────────────────────────────────────────────────────────────────────
print("Creating Chart 6: Forecast...")
fig, ax = plt.subplots(figsize=(12, 5))

C_BLUE  = "#4C72B0"
C_RED   = "#C44E52"
C_GREY  = "#888888"

# Actuals
ax.plot(period_revenue["period"], period_revenue["revenue"],
        color=C_BLUE, linewidth=2, marker="o", markersize=3.5, label="Actual revenue")

# Fitted trend line (actuals range)
ax.plot(period_revenue["period"], y_pred_train,
        color=C_GREY, linewidth=1.2, linestyle="--", alpha=0.7, label="Trend (fitted)")

# Forecast line
ax.plot(forecast_df["period"], forecast_df["forecast"],
        color=C_RED, linewidth=2, linestyle="--", marker="s", markersize=4, label="Forecast")

# Confidence interval shading
ax.fill_between(forecast_df["period"], forecast_df["ci_lower"], forecast_df["ci_upper"],
                color=C_RED, alpha=0.12, label="95% confidence interval")

# Vertical divider between actual and forecast
ax.axvline(x=N_PERIODS + 0.5, color="black", linestyle=":", linewidth=0.8, alpha=0.4)
ax.text(N_PERIODS + 0.6, ax.get_ylim()[0] * 1.05 if ax.get_ylim()[0] > 0 else 1000,
        "Forecast →", fontsize=8, color="gray")

# Annotations for model quality
textstr = f"R² = {r2:.3f}   RMSE = ${rmse:,.0f}"
ax.text(0.02, 0.95, textstr, transform=ax.transAxes,
        fontsize=9, va="top", color=C_GREY,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_GREY, alpha=0.7))

ax.set_title("Revenue Trend & 6-Period Forecast (Linear Regression)")
ax.set_xlabel("Period (sequential order batch)")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))
ax.legend(frameon=False, fontsize=9)

plt.tight_layout()
path = os.path.join(CHARTS_DIR, "chart6_forecast.png")
plt.savefig(path)
plt.close()
print("  Saved: chart6_forecast.png")
print("\nDone.")

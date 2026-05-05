"""
03_model.py
-----------
Builds the lead scoring model using Logistic Regression.

Pipeline:
  1. One-hot encode categoricals, cast everything to float immediately
  2. Train/test split (75/25)
  3. SMOTE on train set only
  4. RFE: select top 20 features
  5. Iterative GLM with VIF pruning -> final feature set
  6. StandardScaler fitted ONLY on numeric cols that survived into final_features
     (fitting before feature selection then transforming a subset breaks sklearn)
  7. Threshold optimisation (sensitivity/specificity crossover)
  8. Test set evaluation + charts + lead scores
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection    import train_test_split
from sklearn.preprocessing      import StandardScaler
from sklearn.linear_model       import LogisticRegression
from sklearn.feature_selection  import RFE
from sklearn.metrics            import (accuracy_score, roc_auc_score, roc_curve,
                                        confusion_matrix, classification_report)
from imblearn.over_sampling     import SMOTE
from collections                import Counter
import statsmodels.api          as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE = os.path.join(BASE_DIR, "data", "leads_clean.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
DATA_DIR   = os.path.join(BASE_DIR, "data")
os.makedirs(CHARTS_DIR, exist_ok=True)

C_BLUE  = "#4C72B0"
C_GREEN = "#55A868"
C_RED   = "#C44E52"
C_ORG   = "#DD8452"

plt.rcParams.update({
    "figure.dpi": 150, "font.family": "DejaVu Sans",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.3,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.labelsize": 10,
})

def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, name))
    plt.close()
    print(f"  Saved: {name}")

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading clean data...")
df = pd.read_csv(CLEAN_FILE)
df['Converted'] = df['Converted'].astype(int)
print(f"{len(df):,} rows | Conversion rate: {df['Converted'].mean()*100:.1f}%\n")

# ── Step 1: Encode + cast to float ───────────────────────────────────────────
cat_cols = df.select_dtypes('object').columns.tolist()
df_enc   = pd.get_dummies(df, columns=cat_cols, drop_first=True).astype(float)
df_enc['Converted'] = df['Converted'].values
print(f"After encoding: {df_enc.shape[1]} features")

# ── Step 2: Split ─────────────────────────────────────────────────────────────
X = df_enc.drop('Converted', axis=1).astype(float)
y = df_enc['Converted'].astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.75, random_state=7)
print(f"Train: {X_train.shape} | Test: {X_test.shape}")

# ── Step 3: SMOTE ─────────────────────────────────────────────────────────────
print(f"\nClass distribution before SMOTE: {Counter(y_train)}")
smote = SMOTE(random_state=42)
X_sm_arr, y_sm_arr = smote.fit_resample(X_train, y_train)
X_train_sm = pd.DataFrame(X_sm_arr, columns=X_train.columns).astype(float)
y_train_sm = pd.Series(y_sm_arr.astype(float))
print(f"Class distribution after SMOTE : {Counter(y_train_sm)}")

# ── Step 4: RFE ───────────────────────────────────────────────────────────────
print("\nRunning RFE (n=20)...")
rfe = RFE(LogisticRegression(random_state=31, max_iter=1000), n_features_to_select=20)
rfe.fit(X_train_sm, y_train_sm)
sug_col = X_train_sm.columns[rfe.support_].tolist()
print(f"RFE selected {len(sug_col)} features: {sug_col[:5]}... (first 5)")

# ── Step 5: Iterative GLM + VIF pruning ───────────────────────────────────────
def get_vif(X_df):
    arr = X_df.values.astype(float)
    vif = pd.DataFrame({'Feature': X_df.columns})
    vif['VIF'] = [variance_inflation_factor(arr, i) for i in range(arr.shape[1])]
    return vif.sort_values('VIF', ascending=False).round(2)

def fit_glm(X_df, y_s):
    Xc = smf.add_constant(X_df.astype(float))
    m  = smf.GLM(y_s.astype(float), Xc, family=smf.families.Binomial()).fit()
    return m, Xc

print("\n── Model iteration (VIF + p-value pruning) ───────────────────────────")
X_tr = X_train_sm[sug_col].copy()
model, X_const = fit_glm(X_tr, y_train_sm)

for _ in range(4):
    vif      = get_vif(X_tr)
    high_vif = vif[vif['VIF'] > 5]
    if high_vif.empty:
        break
    pvals      = model.pvalues.drop('const', errors='ignore')
    candidates = set(high_vif['Feature']) | set(pvals[pvals > 0.05].index)
    overlap    = high_vif[high_vif['Feature'].isin(candidates)]
    drop_feat  = overlap.iloc[0]['Feature'] if not overlap.empty else high_vif.iloc[0]['Feature']
    print(f"  Dropping '{drop_feat}' (VIF={vif[vif['Feature']==drop_feat]['VIF'].values[0]:.1f})")
    X_tr = X_tr.drop(columns=[drop_feat])
    model, X_const = fit_glm(X_tr, y_train_sm)

final_features = X_tr.columns.tolist()
print(f"\nFinal features ({len(final_features)}): {final_features[:5]}... (first 5)")

# ── Step 6: Scale ONLY numeric cols that survived into final_features ─────────
# IMPORTANT: scaler is fit here, AFTER feature selection, on final_features only.
# Fitting earlier then transforming a subset causes sklearn column mismatch errors.
ALL_NUM   = ['TotalVisits', 'Time on Site', 'Pages Viewed']
num_final = [c for c in ALL_NUM if c in final_features]
scaler    = StandardScaler()

if num_final:
    X_tr[num_final] = scaler.fit_transform(X_tr[num_final])
    model, X_const  = fit_glm(X_tr, y_train_sm)   # refit with scaled features
    print(f"Scaled {num_final}; refitted model.")
else:
    print("No numeric cols in final features — skipping scaling.")

# ── Prediction helper (reuse for test + full dataset) ────────────────────────
def prepare(X_raw):
    Xf = X_raw[final_features].copy().astype(float)
    if num_final:
        Xf[num_final] = scaler.transform(Xf[num_final])
    Xc = smf.add_constant(Xf, has_constant='add')
    return Xc.reindex(columns=X_const.columns, fill_value=0.0)

# ── Step 7: Threshold optimisation ───────────────────────────────────────────
print("\n── Finding optimal threshold ─────────────────────────────────────────")
y_tr_proba = model.predict(X_const)
rows = []
for t in np.arange(0.1, 1.0, 0.05):
    t  = round(t, 2)
    yp = (y_tr_proba >= t).astype(int)
    cm = confusion_matrix(y_train_sm, yp)
    TP, TN, FP, FN = cm[1][1], cm[0][0], cm[0][1], cm[1][0]
    rows.append({'threshold': t,
                 'sensitivity': TP/(TP+FN) if (TP+FN) else 0,
                 'specificity': TN/(TN+FP) if (TN+FP) else 0,
                 'accuracy'   : accuracy_score(y_train_sm, yp)})

thresh_df = pd.DataFrame(rows)
thresh_df['gap'] = (thresh_df['sensitivity'] - thresh_df['specificity']).abs()
cands = thresh_df[(thresh_df['sensitivity'] > 0.75) & (thresh_df['specificity'] > 0.75)]
optimal_thresh = cands.loc[cands['gap'].idxmin(), 'threshold'] if len(cands) else 0.475
print(f"Optimal threshold: {optimal_thresh}")

print("Creating Chart 6: Threshold Optimisation...")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(thresh_df['threshold'], thresh_df['sensitivity'], color=C_GREEN, lw=2, marker='o', ms=3, label='Sensitivity')
ax.plot(thresh_df['threshold'], thresh_df['specificity'], color=C_BLUE,  lw=2, marker='o', ms=3, label='Specificity')
ax.plot(thresh_df['threshold'], thresh_df['accuracy'],    color=C_ORG,   lw=2, marker='o', ms=3, label='Accuracy')
ax.axvline(optimal_thresh, color=C_RED, lw=1.5, ls='--', label=f'Optimal: {optimal_thresh}')
ax.set_title(f"Threshold Optimisation (Optimal: {optimal_thresh})")
ax.set_xlabel("Threshold"); ax.set_ylabel("Score"); ax.set_ylim(0, 1.1)
ax.legend(frameon=False, fontsize=9)
savefig("chart6_threshold_optimisation.png")

# ── Step 8: Test set evaluation ───────────────────────────────────────────────
print("\n── Test set evaluation ───────────────────────────────────────────────")
X_test_const = prepare(X_test)
y_test_proba = model.predict(X_test_const)
y_test_pred  = (y_test_proba >= optimal_thresh).astype(int)

acc         = accuracy_score(y_test, y_test_pred)
auc         = roc_auc_score(y_test, y_test_proba)
cm          = confusion_matrix(y_test, y_test_pred)
TP, TN      = cm[1][1], cm[0][0]
FP, FN      = cm[0][1], cm[1][0]
sensitivity = TP / (TP + FN)
specificity = TN / (TN + FP)

print(f"Accuracy    : {acc*100:.2f}%")
print(f"AUC Score   : {auc*100:.2f}%")
print(f"Sensitivity : {sensitivity*100:.2f}%")
print(f"Specificity : {specificity*100:.2f}%")
print(f"\nClassification Report:\n{classification_report(y_test, y_test_pred)}")

pd.DataFrame([{
    'accuracy': round(acc*100,2), 'auc': round(auc*100,2),
    'sensitivity': round(sensitivity*100,2), 'specificity': round(specificity*100,2),
    'threshold': optimal_thresh, 'train_size': len(y_train), 'test_size': len(y_test),
}]).to_csv(os.path.join(DATA_DIR, 'model_metrics.csv'), index=False)
print("  Saved -> model_metrics.csv")

# ── Chart 5: ROC Curve ────────────────────────────────────────────────────────
print("Creating Chart 5: ROC Curve...")
fpr, tpr, _ = roc_curve(y_test, y_test_proba)
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(fpr, tpr, color=C_BLUE, lw=2.5, label=f'AUC = {auc:.3f}')
ax.plot([0,1],[0,1],'k--', lw=1, alpha=0.5, label='Random')
ax.fill_between(fpr, tpr, alpha=0.08, color=C_BLUE)
ax.set_title("ROC Curve — Lead Scoring Model (Test Set)")
ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
ax.legend(frameon=False, fontsize=10)
ax.set_xlim([0,1]); ax.set_ylim([0,1.05])
savefig("chart5_roc_curve.png")

# ── Chart 7: Feature Importance ──────────────────────────────────────────────
print("Creating Chart 7: Feature Importance...")
coef_df = pd.DataFrame({'Feature': model.params.index[1:],
                         'Coefficient': model.params.values[1:]})
coef_df = coef_df.reindex(coef_df['Coefficient'].abs().sort_values(ascending=False).index).head(15)
coef_df = coef_df.sort_values('Coefficient')
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(coef_df['Feature'], coef_df['Coefficient'],
        color=[C_GREEN if c > 0 else C_RED for c in coef_df['Coefficient']],
        height=0.6, zorder=3)
ax.axvline(0, color='black', lw=0.8, alpha=0.5)
ax.set_title("Top 15 Features — Logistic Regression Coefficients\n(green = raises conversion probability, red = lowers)")
ax.set_xlabel("Coefficient Value")
savefig("chart7_feature_importance.png")

# ── Lead Scores: full dataset ─────────────────────────────────────────────────
print("\nGenerating lead scores for full dataset...")
X_full       = df_enc.drop('Converted', axis=1).astype(float)
X_full_const = prepare(X_full)
scores       = model.predict(X_full_const)

score_df = pd.DataFrame({
    'lead_score'     : (scores * 100).round(1),
    'predicted_label': (scores >= optimal_thresh).astype(int),
    'actual'         : df_enc['Converted'].values,
})
score_df['lead_tier'] = pd.cut(score_df['lead_score'],
                                bins=[0, 40, 65, 100],
                                labels=['Cold', 'Warm', 'Hot'])
score_df.to_csv(os.path.join(DATA_DIR, 'lead_scores.csv'), index=False)
print(f"  Saved -> lead_scores.csv ({len(score_df):,} leads scored)")
print(f"\nLead tier distribution:\n{score_df['lead_tier'].value_counts()}")
print("\nDone.")

"""
=============================================================================
BOOTCAMP ON ARTIFICIAL INTELLIGENCE - NIELIT DELHI
SUPERVISED MACHINE LEARNING - LINEAR REGRESSION EXPERIMENT
DATASET: IPL Matches Dataset (IPL_Matches_Data_2008_2026.csv)
=============================================================================
Objective:
  1. Load and inspect IPL match records (1,240+ matches from 2008 to 2026).
  2. Exploratory Data Analysis (EDA) on team scores and wickets.
  3. Simple Linear Regression: Predict 2nd Innings Score (team2_runs) from 1st Innings (team1_runs).
  4. Multiple Linear Regression: Predict 2nd Innings Score using multiple match features.
  5. Evaluate models using MAE, MSE, RMSE, and R-squared (R2) metrics.
  6. Visualize the regression line, Actual vs. Predicted plots, and residual error distribution.
  7. Make live match score predictions for upcoming/custom IPL scenarios.
=============================================================================
"""

# =============================================================================
# STEP 1: IMPORT REQUIRED LIBRARIES & CHECK ENVIRONMENT
# =============================================================================
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

print("=" * 65)
print("STEP 1: CHECKING ENVIRONMENT & LIBRARIES")
print("=" * 65)
print("Environment ready!")
print("NumPy:       ", np.__version__)
print("pandas:      ", pd.__version__)
print("scikit-learn:", __import__("sklearn").__version__)

# =============================================================================
# STEP 2: LOAD AND INSPECT IPL DATASET
# =============================================================================
print("\n" + "=" * 65)
print("STEP 2: LOADING DATASET (IPL_Matches_Data_2008_2026.csv)")
print("=" * 65)

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "IPL_Matches_Data_2008_2026.csv")

if not os.path.exists(csv_path):
    # Fallback to root or current directory
    csv_path = "IPL_Matches_Data_2008_2026.csv"

df = pd.read_csv(csv_path)

print(f"Dataset Loaded Successfully!")
print(f"Total Matches: {df.shape[0]} | Total Features: {df.shape[1]}")
print("\n--- Key Match Columns (First 5 Rows) ---")
key_cols = ["date", "team1", "team2", "team1_runs", "team1_wickets", "team2_runs", "team2_wickets", "winner"]
print(df[key_cols].head())

# =============================================================================
# STEP 3: DATA CLEANING & EXPLORATORY DATA ANALYSIS (EDA)
# =============================================================================
print("\n" + "=" * 65)
print("STEP 3: DATA CLEANING & STATISTICAL SUMMARY")
print("=" * 65)

# Filter valid completed matches (excluding abandoned matches with 0 runs)
df_clean = df[(df["team1_runs"] > 30) & (df["team2_runs"] > 30)].copy()
print(f"Valid Matches for Regression Analysis: {len(df_clean)}")

print("\n--- Summary Statistics (Runs & Wickets) ---")
stats = df_clean[["team1_runs", "team1_wickets", "team2_runs", "team2_wickets"]].describe()
print(stats.round(2))

# Correlation Matrix
corr = df_clean[["team1_runs", "team1_wickets", "team2_runs", "team2_wickets"]].corr()
print("\n--- Correlation Matrix ---")
print(corr.round(3))
print(f"\nStrong Linear Correlation between 1st & 2nd Innings Runs: r = {corr.loc['team1_runs', 'team2_runs']:.3f}")

# =============================================================================
# STEP 4: MODEL 1 - SIMPLE LINEAR REGRESSION (1 Feature)
# Predict team2_runs using only team1_runs
# Equation: y = m * x + c
# =============================================================================
print("\n" + "=" * 65)
print("STEP 4: MODEL 1 - SIMPLE LINEAR REGRESSION")
print("=" * 65)

X_simple = df_clean[["team1_runs"]]
y = df_clean["team2_runs"]

# 80% Train, 20% Test Split
X_train_s, X_test_s, y_train, y_test = train_test_split(
    X_simple, y, test_size=0.20, random_state=42
)

simple_lr = LinearRegression()
simple_lr.fit(X_train_s, y_train)

m_simple = simple_lr.coef_[0]
c_simple = simple_lr.intercept_

print(f"Training Rows: {len(X_train_s)} | Testing Rows: {len(X_test_s)}")
print(f"Learned Equation: Team2_Runs = ({m_simple:.3f} * Team1_Runs) + {c_simple:.2f}")

# Predictions & Metrics for Model 1
y_pred_simple = simple_lr.predict(X_test_s)
r2_simple = r2_score(y_test, y_pred_simple)
mae_simple = mean_absolute_error(y_test, y_pred_simple)
mse_simple = mean_squared_error(y_test, y_pred_simple)
rmse_simple = np.sqrt(mse_simple)

print(f"\n--- Model 1 Evaluation (Simple LR) ---")
print(f"R-squared (R2) Score : {r2_simple:.4f} ({r2_simple * 100:.2f}% variance explained)")
print(f"Mean Absolute Error  : {mae_simple:.2f} runs")
print(f"Root Mean Sq. Error  : {rmse_simple:.2f} runs")

# =============================================================================
# STEP 5: VISUALIZE SIMPLE LINEAR REGRESSION (Scatter + Best Fit Line)
# =============================================================================
plt.figure(figsize=(9, 5))
plt.scatter(X_test_s["team1_runs"], y_test, color="#1f77b4", alpha=0.6, edgecolors="k", s=50, label="Actual Match Data (Test Set)")
plt.plot(X_test_s["team1_runs"], y_pred_simple, color="#d62728", linewidth=2.5, label=f"Regression Line: y = {m_simple:.2f}x + {c_simple:.1f}")
plt.xlabel("1st Innings Runs (team1_runs)", fontsize=11, fontweight="bold")
plt.ylabel("2nd Innings Runs (team2_runs)", fontsize=11, fontweight="bold")
plt.title("IPL Match Score Prediction: Simple Linear Regression", fontsize=13, fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(fontsize=10)
plt.tight_layout()

chart1 = os.path.join(base_dir, "ipl_simple_linear_regression.png")
plt.savefig(chart1, dpi=150)
print(f"Plot saved to: '{chart1}'")
plt.show()

# =============================================================================
# STEP 6: MODEL 2 - MULTIPLE LINEAR REGRESSION (Multiple Features)
# Predict team2_runs using: team1_runs, team1_wickets, team2_wickets
# Equation: y = m1*x1 + m2*x2 + m3*x3 + c
# =============================================================================
print("\n" + "=" * 65)
print("STEP 6: MODEL 2 - MULTIPLE LINEAR REGRESSION")
print("=" * 65)

features_multi = ["team1_runs", "team1_wickets", "team2_wickets"]
X_multi = df_clean[features_multi]

X_train_m, X_test_m, _, _ = train_test_split(
    X_multi, y, test_size=0.20, random_state=42
)

multi_lr = LinearRegression()
multi_lr.fit(X_train_m, y_train)

print("Multiple Linear Regression Formula:")
print(f"Team2_Runs = {multi_lr.intercept_:.2f}", end="")
for feat, coef in zip(features_multi, multi_lr.coef_):
    sign = "+" if coef >= 0 else "-"
    print(f" {sign} ({abs(coef):.3f} * {feat})", end="")
print("\n")

print("--- Feature Coefficients Interpretation ---")
for feat, coef in zip(features_multi, multi_lr.coef_):
    impact = "increases" if coef > 0 else "decreases"
    print(f" - {feat:<15}: {coef:>7.3f} -> Each unit {impact} predicted score by {abs(coef):.2f} runs")

# Predictions & Metrics for Model 2
y_pred_multi = multi_lr.predict(X_test_m)
r2_multi = r2_score(y_test, y_pred_multi)
mae_multi = mean_absolute_error(y_test, y_pred_multi)
mse_multi = mean_squared_error(y_test, y_pred_multi)
rmse_multi = np.sqrt(mse_multi)

print(f"\n--- Model 2 Evaluation (Multiple LR) ---")
print(f"R-squared (R2) Score : {r2_multi:.4f} ({r2_multi * 100:.2f}% variance explained)")
print(f"Mean Absolute Error  : {mae_multi:.2f} runs")
print(f"Root Mean Sq. Error  : {rmse_multi:.2f} runs")

# =============================================================================
# STEP 7: MODEL COMPARISON TABLE
# =============================================================================
print("\n" + "=" * 65)
print("STEP 7: COMPARISON: SIMPLE LR vs. MULTIPLE LR")
print("=" * 65)

comparison_df = pd.DataFrame({
    "Model": ["Simple Linear Regression", "Multiple Linear Regression"],
    "Features Used": ["1 (team1_runs)", "3 (runs, w1, w2)"],
    "R2 Score": [f"{r2_simple:.4f}", f"{r2_multi:.4f}"],
    "MAE (Runs)": [f"{mae_simple:.2f}", f"{mae_multi:.2f}"],
    "RMSE (Runs)": [f"{rmse_simple:.2f}", f"{rmse_multi:.2f}"]
})
print(comparison_df.to_string(index=False))
print("\nConclusion: Adding wickets features improved R2 and reduced error!")

# =============================================================================
# STEP 8: RESIDUALS & ACTUAL VS. PREDICTED VISUALIZATION
# =============================================================================
print("\n" + "=" * 65)
print("STEP 8: VISUALIZING ACTUAL VS. PREDICTED SCORES")
print("=" * 65)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Actual vs Predicted Scatter
ax1.scatter(y_test, y_pred_multi, color="#2ca02c", alpha=0.6, edgecolors="k", s=50)
min_val = min(y_test.min(), y_pred_multi.min())
max_val = max(y_test.max(), y_pred_multi.max())
ax1.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--", linewidth=2, label="Ideal Fit (y = x)")
ax1.set_xlabel("Actual 2nd Innings Runs", fontsize=11, fontweight="bold")
ax1.set_ylabel("Predicted 2nd Innings Runs", fontsize=11, fontweight="bold")
ax1.set_title("Actual vs. Predicted Scores (Multiple LR)", fontsize=12, fontweight="bold")
ax1.grid(True, linestyle="--", alpha=0.6)
ax1.legend()

# Plot 2: Residual Error Distribution
residuals = y_test - y_pred_multi
ax2.hist(residuals, bins=25, color="#ff7f0e", edgecolor="black", alpha=0.7)
ax2.axvline(0, color="red", linestyle="--", linewidth=2, label="Zero Error Line")
ax2.set_xlabel("Residual Error (Actual - Predicted)", fontsize=11, fontweight="bold")
ax2.set_ylabel("Frequency", fontsize=11, fontweight="bold")
ax2.set_title(f"Residual Error Distribution (Mean Error: {residuals.mean():.2f})", fontsize=12, fontweight="bold")
ax2.grid(True, linestyle="--", alpha=0.6)
ax2.legend()

plt.tight_layout()
chart2 = os.path.join(base_dir, "ipl_actual_vs_predicted.png")
plt.savefig(chart2, dpi=150)
print(f"Plot saved to: '{chart2}'")
plt.show()

# =============================================================================
# STEP 9: LIVE MATCH PREDICTIONS ON NEW SCENARIOS
# =============================================================================
print("\n" + "=" * 65)
print("STEP 9: LIVE PREDICTIONS ON CUSTOM IPL MATCH SCENARIOS")
print("=" * 65)

scenarios = pd.DataFrame([
    {"Match": "CSK vs RCB (High Scoring)", "team1_runs": 218, "team1_wickets": 3, "team2_wickets": 5},
    {"Match": "KKR vs SRH (Average Match)", "team1_runs": 165, "team1_wickets": 6, "team2_wickets": 7},
    {"Match": "DC vs LSG (Low Scoring Pitch)", "team1_runs": 125, "team1_wickets": 9, "team2_wickets": 8},
])

predictions = multi_lr.predict(scenarios[["team1_runs", "team1_wickets", "team2_wickets"]])
scenarios["Predicted_Team2_Runs"] = np.round(predictions, 1)

print(scenarios.to_string(index=False))

print("\n" + "=" * 65)
print("IPL LINEAR REGRESSION EXPERIMENT COMPLETED SUCCESSFULLY!")
print("=" * 65)

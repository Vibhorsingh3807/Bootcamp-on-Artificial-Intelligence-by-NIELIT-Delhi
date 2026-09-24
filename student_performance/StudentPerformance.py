"""
=============================================================================
BOOTCAMP ON ARTIFICIAL INTELLIGENCE - NIELIT DELHI
DAY 3: SUPERVISED MACHINE LEARNING - DECISION TREE CLASSIFIER
DATASET: Student Performance (student_performance.csv)
=============================================================================
Objective:
  1. Load and explore student performance data (study_hours, attendance, assignments, result).
  2. Perform Exploratory Data Analysis (EDA) and visualize patterns.
  3. Split data into Training and Testing sets (train_test_split with stratification).
  4. Train a Decision Tree Classifier (max_depth=3).
  5. Evaluate the model using Accuracy, Confusion Matrix, and Classification Report.
  6. Visualize the Decision Tree structure (plot_tree).
  7. Make live predictions on new student scenarios.
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
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

print("=" * 60)
print("STEP 1: CHECKING ENVIRONMENT & LIBRARIES")
print("=" * 60)
print("Environment ready!")
print("NumPy:       ", np.__version__)
print("pandas:      ", pd.__version__)
print("scikit-learn:", __import__("sklearn").__version__)

# =============================================================================
# STEP 2: LOAD DATASET
# =============================================================================
print("\n" + "=" * 60)
print("STEP 2: LOADING DATASET (student_performance.csv)")
print("=" * 60)

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "student_performance.csv")

if not os.path.exists(csv_path):
    # Fallback to current working directory
    csv_path = "student_performance.csv"

df = pd.read_csv(csv_path)

print(f"Dataset successfully loaded! Total rows: {len(df)}, Total columns: {len(df.columns)}")
print("\n--- First 5 Rows (df.head()) ---")
print(df.head())

# =============================================================================
# STEP 3: EXPLORATORY DATA ANALYSIS (EDA) & VISUALIZATION
# =============================================================================
print("\n" + "=" * 60)
print("STEP 3: EXPLORATORY DATA ANALYSIS (EDA)")
print("=" * 60)

print("\n--- Groupby Mean per Result (0 = Fail, 1 = Pass) ---")
grouped_stats = df.groupby("result")[["study_hours", "attendance", "assignments"]].mean()
print(grouped_stats)

# Visualizing Student Performance Pattern with Scatter Plot
plt.figure(figsize=(8, 5))
scatter = plt.scatter(
    df["study_hours"], 
    df["attendance"], 
    c=df["result"], 
    cmap="coolwarm", 
    edgecolors="k", 
    s=70, 
    alpha=0.85
)
cbar = plt.colorbar(scatter, ticks=[0, 1])
cbar.set_ticklabels(["Fail (0)", "Pass (1)"])
cbar.set_label("Exam Result", fontsize=11, fontweight="bold")

plt.xlabel("Study Hours (Daily)", fontsize=11, fontweight="bold")
plt.ylabel("Attendance Percentage (%)", fontsize=11, fontweight="bold")
plt.title("Student Performance Pattern: Study Hours vs. Attendance", fontsize=13, fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

scatter_chart_file = os.path.join(base_dir, "student_performance_scatter.png")
plt.savefig(scatter_chart_file, dpi=150)
print(f"\nScatter plot successfully saved to: '{scatter_chart_file}'")
plt.show()

# =============================================================================
# STEP 4: PREPARE FEATURES (X) AND TARGET (y)
# =============================================================================
print("\n" + "=" * 60)
print("STEP 4: PREPARING FEATURES (X) AND TARGET (y)")
print("=" * 60)

# Features: inputs used for prediction
X = df[["study_hours", "attendance", "assignments"]]

# Target: class label to predict (0 = Fail, 1 = Pass)
y = df["result"]

print("Features (X) columns:", list(X.columns))
print("X shape:", X.shape)
print("y shape:", y.shape)

# =============================================================================
# STEP 5: TRAIN / TEST SPLIT (80% Training, 20% Testing)
# =============================================================================
print("\n" + "=" * 60)
print("STEP 5: SPLITTING DATA INTO TRAIN AND TEST SETS")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Total Records  : {len(X)}")
print(f"Training rows  : {len(X_train)} (80%)")
print(f"Testing rows   : {len(X_test)} (20%)")
print(f"Training Class Distribution:\n{y_train.value_counts()}")

# =============================================================================
# STEP 6: TRAIN DECISION TREE CLASSIFIER MODEL
# =============================================================================
print("\n" + "=" * 60)
print("STEP 6: TRAINING DECISION TREE CLASSIFIER")
print("=" * 60)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

print("Model trained successfully!")

# Feature Importances learned by Decision Tree
feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)
print("\n--- Feature Importances ---")
print(feature_importance.to_string(index=False))

# =============================================================================
# STEP 7: MODEL EVALUATION ON UNSEEN TEST DATA
# =============================================================================
print("\n" + "=" * 60)
print("STEP 7: MODEL EVALUATION ON TEST DATA (20%)")
print("=" * 60)

# Make predictions on test set
y_pred = model.predict(X_test)

# Calculate Evaluation Metrics
acc = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)
cr = classification_report(y_test, y_pred, target_names=["Fail (0)", "Pass (1)"])

print(f"Accuracy Score: {acc * 100:.2f}%\n")

print("Confusion Matrix:")
print("                 Predicted Fail   Predicted Pass")
print(f"Actual Fail  :        {cm[0][0]:<15} {cm[0][1]}")
print(f"Actual Pass  :        {cm[1][0]:<15} {cm[1][1]}")

print("\n--- Classification Report ---")
print(cr)

# =============================================================================
# STEP 8: VISUALIZE THE DECISION TREE (plot_tree)
# =============================================================================
print("=" * 60)
print("STEP 8: VISUALIZING THE DECISION TREE")
print("=" * 60)

plt.figure(figsize=(14, 8))
plot_tree(
    model,
    feature_names=["study_hours", "attendance", "assignments"],
    class_names=["Fail (0)", "Pass (1)"],
    filled=True,
    rounded=True,
    fontsize=10
)
plt.title("Decision Tree for Student Performance Prediction (max_depth=3)", fontsize=14, fontweight="bold")
plt.tight_layout()

tree_chart_file = os.path.join(base_dir, "student_decision_tree.png")
plt.savefig(tree_chart_file, dpi=200)
print(f"Decision tree diagram saved to: '{tree_chart_file}'")
plt.show()

# =============================================================================
# STEP 9: LIVE PREDICTIONS ON NEW STUDENT DATA
# =============================================================================
print("\n" + "=" * 60)
print("STEP 9: TESTING LIVE PREDICTIONS ON NEW STUDENTS")
print("=" * 60)

new_students = pd.DataFrame([
    {"name": "Aarav", "study_hours": 7.5, "attendance": 90, "assignments": 9},  # High effort -> should pass
    {"name": "Sneha", "study_hours": 2.0, "attendance": 60, "assignments": 2},  # Low effort -> should fail
    {"name": "Rohan", "study_hours": 4.5, "attendance": 78, "assignments": 6},  # Borderline case
])

predictions = model.predict(new_students[["study_hours", "attendance", "assignments"]])
probabilities = model.predict_proba(new_students[["study_hours", "attendance", "assignments"]])

new_students["Predicted_Result"] = ["Pass (1)" if p == 1 else "Fail (0)" for p in predictions]
new_students["Pass_Probability"] = [f"{prob[1] * 100:.1f}%" for prob in probabilities]

print(new_students[["name", "study_hours", "attendance", "assignments", "Predicted_Result", "Pass_Probability"]].to_string(index=False))

print("\n" + "=" * 60)
print("EXPERIMENT COMPLETED SUCCESSFULLY!")
print("=" * 60)

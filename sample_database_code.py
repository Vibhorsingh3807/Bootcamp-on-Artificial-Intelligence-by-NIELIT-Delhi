import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# ==========================================================
# STEP 1: LOAD DATA DIRECTLY FROM YOUR SAMPLE DATABASE
# ==========================================================
conn = sqlite3.connect("satellite_data.db")

# Load data into pandas DataFrame
df = pd.read_sql_query("SELECT * FROM band_catalog", conn)
conn.close()

print("Dataset loaded from satellite_data.db:")
print(df[["band_name", "temperature_celsius", "radiance_lmax", "file_size_mb"]])

# ==========================================================
# STEP 2: DEFINE A TARGET CLASS FOR MACHINE LEARNING
# Example: Classify bands as 'High_Heat' (1) if temp > 18°C, else 'Normal_Heat' (0)
# ==========================================================
df["heat_class"] = (df["temperature_celsius"] > 18.0).astype(int)

# Features (X) and Target (y)
X = df[["temperature_celsius", "radiance_lmax", "file_size_mb"]]
y = df["heat_class"]

# ==========================================================
# STEP 3: TRAIN / TEST SPLIT
# ==========================================================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# ==========================================================
# STEP 4: TRAIN THE DECISION TREE CLASSIFIER
# ==========================================================
clf = DecisionTreeClassifier(criterion="gini", max_depth=3, random_state=42)
clf.fit(X_train, y_train)

# ==========================================================
# STEP 5: PREDICTIONS & EVALUATION METRICS
# ==========================================================
y_pred = clf.predict(X_test)

print("\n--- Model Evaluation ---")
print("Accuracy Score:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))

# ==========================================================
# STEP 6: VISUALIZE THE DECISION TREE USING MATPLOTLIB
# ==========================================================
plt.figure(figsize=(8, 6))
plot_tree(
    clf, 
    feature_names=["Temperature", "Radiance_Lmax", "FileSize"], 
    class_names=["Normal_Heat", "High_Heat"], 
    filled=True, 
    rounded=True
)
plt.title("Decision Tree Trained on Satellite Database Features")
plt.show()

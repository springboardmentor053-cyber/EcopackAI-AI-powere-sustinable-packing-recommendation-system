

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


# Step 0: Set data folder

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_folder = os.path.join(project_root, "data")

if not os.path.exists(data_folder):
    raise FileNotFoundError(f"Data folder not found: {data_folder}")

print("✅ Milestone 2: ML pipeline started")
print("Data folder:", data_folder)


# Step 1: Load datasets

materials_file = os.path.join(data_folder, "materials_processed_80rows.csv")
products_file = os.path.join(data_folder, "products_80rows.csv")

if not os.path.exists(materials_file):
    raise FileNotFoundError(f"Materials file not found: {materials_file}")
if not os.path.exists(products_file):
    raise FileNotFoundError(f"Products file not found: {products_file}")

print(" Loading datasets...")
df_materials = pd.read_csv(materials_file)
df_products = pd.read_csv(products_file)

print("Materials shape:", df_materials.shape)
print("Products shape:", df_products.shape)

if 'material_name' not in df_materials.columns:
    df_materials['material_name'] = ['Material_' + str(i+1) for i in range(len(df_materials))]


# Step 2: Select features & targets

features = ['strength', 'weight_capacity', 'biodegradability_score', 'recyclability_percentage']
target_cost = 'cost_per_unit'
target_co2 = 'co2_emission_score'

X = df_materials[features]
y_cost = df_materials[target_cost]
y_co2 = df_materials[target_co2]

# -----------------------------
# Step 2a: Train-test split (80%-20%)
# -----------------------------
X_train, X_test, y_cost_train, y_cost_test, y_co2_train, y_co2_test = train_test_split(
    X, y_cost, y_co2, test_size=0.2, random_state=42
)

# -----------------------------
# Step 3: Scale features
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# Step 4: Random Forest for Cost
# -----------------------------
print(" Training Random Forest Regressor for Cost Prediction...")

rf_cost = RandomForestRegressor(
    n_estimators=500, 
    max_depth=None,
    random_state=42
)
rf_cost.fit(X_train_scaled, y_cost_train)
y_cost_pred = rf_cost.predict(X_test_scaled)

print("\nCost Prediction Metrics:")
print("RMSE:", round(np.sqrt(mean_squared_error(y_cost_test, y_cost_pred)), 4))
print("MAE:", round(mean_absolute_error(y_cost_test, y_cost_pred), 4))
print("R2 Score:", round(r2_score(y_cost_test, y_cost_pred), 4))

# -----------------------------
# Step 5: XGBoost for CO2
# -----------------------------
print(" Training XGBoost Regressor for CO₂ Prediction...")

xgb_co2 = XGBRegressor(
    n_estimators=500,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
xgb_co2.fit(X_train_scaled, y_co2_train)
y_co2_pred = xgb_co2.predict(X_test_scaled)

print("\nCO₂ Prediction Metrics:")
print("RMSE:", round(np.sqrt(mean_squared_error(y_co2_test, y_co2_pred)), 4))
print("MAE:", round(mean_absolute_error(y_co2_test, y_co2_pred), 4))
print("R2 Score:", round(r2_score(y_co2_test, y_co2_pred), 4))

# -----------------------------
# Step 6: Generate Material Suitability Score
# -----------------------------
print(" Generating Material Suitability Scores...")

# Predict for all materials
X_scaled_full = scaler.transform(X)
df_materials['pred_cost'] = rf_cost.predict(X_scaled_full)
df_materials['pred_co2'] = xgb_co2.predict(X_scaled_full)

# Normalize predictions 
df_materials['norm_cost'] = (df_materials['pred_cost'].max() - df_materials['pred_cost']) / \
                            (df_materials['pred_cost'].max() - df_materials['pred_cost'].min())
df_materials['norm_co2'] = (df_materials['pred_co2'].max() - df_materials['pred_co2']) / \
                           (df_materials['pred_co2'].max() - df_materials['pred_co2'].min())

# Combine scores
df_materials['material_suitability_score'] = df_materials['norm_cost'] * 0.5 + df_materials['norm_co2'] * 0.5

# Sort materials
df_materials_sorted = df_materials.sort_values(by='material_suitability_score', ascending=False)

print("\nTop 10 Materials by Suitability Score:")
print(df_materials_sorted[['material_name', 'material_suitability_score']].head(10))

# -----------------------------
# Step 7: Save ML-ready dataset
# -----------------------------
ml_ready_file = os.path.join(data_folder, "materials_ml_ready.csv")
df_materials_sorted.to_csv(ml_ready_file, index=False)
print(f" ML-ready dataset saved at: {ml_ready_file}")

print(" Milestone 2 completed successfully!")

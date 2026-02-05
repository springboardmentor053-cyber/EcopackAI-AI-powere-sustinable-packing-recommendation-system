import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os

# ============ LOAD DATA ============

X_train = pd.read_csv('data/processed/X_train.csv')
X_test = pd.read_csv('data/processed/X_test.csv')
y_train = pd.read_csv('data/processed/y_train.csv')
y_test = pd.read_csv('data/processed/y_test.csv')

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"Features: {X_train.shape[1]}")

# ============ HELPER FUNCTION ============

def evaluate_model(name, y_true, y_pred):
    """Calculate and print evaluation metrics"""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    print(f"\n{name}:")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  R²:   {r2:.4f}")
    
    return {'rmse': rmse, 'mae': mae, 'r2': r2}

# ============ MODEL 1: SUITABILITY SCORE (Random Forest) ============

print("\n" + "=" * 70)
print("MODEL 1: SUITABILITY SCORE PREDICTION (Random Forest)")
print("=" * 70)

rf_suitability = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

rf_suitability.fit(X_train, y_train['suitability_score'])
y_pred_suitability = rf_suitability.predict(X_test)

metrics_suitability = evaluate_model(
    "Suitability Score Model",
    y_test['suitability_score'],
    y_pred_suitability
)

# ============ MODEL 2: CO2 PREDICTION (XGBoost) ============

print("\n" + "=" * 70)
print("MODEL 2: CO₂ FOOTPRINT PREDICTION (XGBoost)")
print("=" * 70)

xgb_co2 = XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1
)

xgb_co2.fit(X_train, y_train['predicted_co2'])
y_pred_co2 = xgb_co2.predict(X_test)

metrics_co2 = evaluate_model(
    "CO₂ Prediction Model",
    y_test['predicted_co2'],
    y_pred_co2
)

# ============ MODEL 3: COST PREDICTION (Random Forest) ============

print("\n" + "=" * 70)
print("MODEL 3: COST PREDICTION (Random Forest)")
print("=" * 70)

rf_cost = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

rf_cost.fit(X_train, y_train['predicted_cost'])
y_pred_cost = rf_cost.predict(X_test)

metrics_cost = evaluate_model(
    "Cost Prediction Model",
    y_test['predicted_cost'],
    y_pred_cost
)

# ============ FEATURE IMPORTANCE ============

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE (Suitability Model)")
print("=" * 70)

feature_names = X_train.columns.tolist()
importances = rf_suitability.feature_importances_
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': importances
}).sort_values('importance', ascending=False)

print(importance_df.to_string(index=False))

# ============ SAVE MODELS ============

os.makedirs('ml/models', exist_ok=True)

joblib.dump(rf_suitability, 'ml/models/rf_suitability.pkl')
joblib.dump(xgb_co2, 'ml/models/xgb_co2.pkl')
joblib.dump(rf_cost, 'ml/models/rf_cost.pkl')

print("\n" + "=" * 70)
print("MODELS SAVED")
print("=" * 70)
print("✓ ml/models/rf_suitability.pkl")
print("✓ ml/models/xgb_co2.pkl")
print("✓ ml/models/rf_cost.pkl")

# ============ SUMMARY ============

print("\n" + "=" * 70)
print("TRAINING SUMMARY")
print("=" * 70)
print(f"{'Model':<30} {'RMSE':<12} {'MAE':<12} {'R²':<12}")
print("-" * 70)
print(f"{'Suitability (Random Forest)':<30} {metrics_suitability['rmse']:<12.4f} {metrics_suitability['mae']:<12.4f} {metrics_suitability['r2']:<12.4f}")
print(f"{'CO₂ (XGBoost)':<30} {metrics_co2['rmse']:<12.4f} {metrics_co2['mae']:<12.4f} {metrics_co2['r2']:<12.4f}")
print(f"{'Cost (Random Forest)':<30} {metrics_cost['rmse']:<12.4f} {metrics_cost['mae']:<12.4f} {metrics_cost['r2']:<12.4f}")
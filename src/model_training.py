import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Configuration
PROCESSED_DATA_DIR = 'data/final'
ARTIFACTS_DIR = 'models_artifacts'

def load_data():
    print("Loading prepared data...")
    X_train = np.load(os.path.join(PROCESSED_DATA_DIR, 'X_train.npy'))
    X_test = np.load(os.path.join(PROCESSED_DATA_DIR, 'X_test.npy'))
    
    y_cost_train = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'y_cost_train.csv')).values.ravel()
    y_cost_test = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'y_cost_test.csv')).values.ravel()
    
    y_co2_train = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'y_co2_train.csv')).values.ravel()
    y_co2_test = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'y_co2_test.csv')).values.ravel()
    
    return X_train, X_test, y_cost_train, y_cost_test, y_co2_train, y_co2_test

def evaluate_model(model, X_test, y_test, name="Model"):
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"\n--- {name} Evaluation ---")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    return {'rmse': rmse, 'mae': mae, 'r2': r2}

def train_models():
    X_train, X_test, y_cost_train, y_cost_test, y_co2_train, y_co2_test = load_data()
    
    # 1. Train Cost Prediction Model (Random Forest)
    print("\nTraining Cost Prediction Model (Random Forest)...")
    cost_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    cost_model.fit(X_train, y_cost_train)
    evaluate_model(cost_model, X_test, y_cost_test, "Cost Prediction Model")
    
    # Save Cost Model
    joblib.dump(cost_model, os.path.join(ARTIFACTS_DIR, 'cost_model.pkl'))
    print("Cost model saved.")
    
    # 2. Train CO2 Prediction Model (XGBoost)
    print("\nTraining CO2 Prediction Model (XGBoost)...")
    co2_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    co2_model.fit(X_train, y_co2_train)
    evaluate_model(co2_model, X_test, y_co2_test, "CO2 Prediction Model")
    
    # Save CO2 Model
    joblib.dump(co2_model, os.path.join(ARTIFACTS_DIR, 'co2_model.pkl'))
    print("CO2 model saved.")

if __name__ == "__main__":
    train_models()

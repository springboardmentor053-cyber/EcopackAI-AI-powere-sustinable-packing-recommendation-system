
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import xgboost as xgb
from .db_service import db_service
from .ml_service import ml_service

class TrainingService:
    def __init__(self):
        # Paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.abspath(os.path.join(self.base_dir, '..', '..', '..', 'models'))
        self.cost_model_path = os.path.join(self.model_dir, 'cost_predictor_model.pkl')
        self.co2_model_path = os.path.join(self.model_dir, 'co2_predictor_model.pkl')

    def retrain_models(self):
        """
        Fetches data from 'features_engineering', retrains models, saves them, and reloads MLService.
        """
        engine = db_service.get_engine()
        print("🔄 Starting Model Retraining...")

        # 1. Fetch Data
        query = "SELECT * FROM features_engineering"
        try:
            df = pd.read_sql(query, engine)
        except Exception as e:
            return {"success": False, "message": f"Database read failed: {str(e)}"}

        if df.empty:
            return {"success": False, "message": "No data available for training."}

        # 2. Prepare Data
        # Features & Targets
        features = ['strength', 'weight_capacity_kg', 'biodegradability_score', 'recyclability_percent', 'water_resistance', 'material_type']
        target_cost = 'cost_per_unit_inr'
        target_co2 = 'co2_emission_score'

        X = df[features]
        y_cost = df[target_cost]
        y_co2 = df[target_co2]

        # Preprocessing Pipeline
        numeric_features = ['strength', 'weight_capacity_kg', 'biodegradability_score', 'recyclability_percent', 'water_resistance']
        categorical_features = ['material_type']

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            # Handle unknown categories by ignoring them
            ('encoder', OneHotEncoder(handle_unknown='ignore')) 
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])

        # 3. Train Cost Model (Random Forest)
        cost_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))])
        
        print("   Training Cost Model...")
        cost_pipeline.fit(X, y_cost)

        # 4. Train CO2 Model (XGBoost)
        co2_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                       ('regressor', xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42))])
        
        print("   Training CO2 Model...")
        co2_pipeline.fit(X, y_co2)

        # 5. Save Models
        try:
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
            
            joblib.dump(cost_pipeline, self.cost_model_path)
            joblib.dump(co2_pipeline, self.co2_model_path)
            print("✅ Models saved.")
        except Exception as e:
            return {"success": False, "message": f"Failed to save models: {str(e)}"}

        # 6. Reload Live Service
        ml_service._load_models()

        return {"success": True, "message": "Models successfully retrained and reloaded."}

training_service = TrainingService()


import pandas as pd
import numpy as np
import joblib
import psycopg2
from sqlalchemy import create_engine
import os

# Helper to get absolute path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'models')

# Database Config
DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecopackai_db"

class MaterialRecommender:
    def __init__(self):
        self.cost_model = None
        self.co2_model = None
        self.engine = None
        self._load_models()
        self._connect_db()

    def _load_models(self):
        """Load trained ML models from .pkl files."""
        try:
            cost_model_path = os.path.join(MODEL_DIR, 'cost_predictor_model.pkl')
            co2_model_path = os.path.join(MODEL_DIR, 'co2_predictor_model.pkl')
            
            if not os.path.exists(cost_model_path) or not os.path.exists(co2_model_path):
                raise FileNotFoundError("Model files not found. Please train models first.")

            self.cost_model = joblib.load(cost_model_path)
            self.co2_model = joblib.load(co2_model_path)
            print("✅ Models loaded successfully.")
        except Exception as e:
            print(f"❌ Error loading models: {e}")

    def _connect_db(self):
        """Establish database connection."""
        try:
            connection_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            self.engine = create_engine(connection_str)
            print("✅ Database connection established.")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

    def get_recommendations(self, product_weight_kg, product_category, top_n=5):
        """
        Recommend materials based on product constraints and ML predictions.
        
        Args:
            product_weight_kg (float): Weight of the product.
            product_category (str): Category (e.g., 'Electronics', 'Food').
            top_n (int): Number of recommendations to return.
            
        Returns:
            pd.DataFrame: Top N recommended materials with scores.
        """
        if self.engine is None:
            return pd.DataFrame()

        # 1. Fetch Candidate Materials from DB
        # We perform a basic filter in SQL for weight capacity
        query = f"""
        SELECT 
            material_id, 
            material_type, 
            strength, 
            weight_capacity_kg, 
            biodegradability_score, 
            recyclability_percent, 
            water_resistance
        FROM materials
        WHERE weight_capacity_kg >= {product_weight_kg}
        """
        
        try:
            candidates_df = pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"❌ Error fetching candidates: {e}")
            return pd.DataFrame()

        if candidates_df.empty:
            print("⚠️ No materials found matching the weight criteria.")
            return pd.DataFrame()

        # 2. Prepare Features for Prediction
        # Columns must match training: 
        # ['strength', 'weight_capacity_kg', 'biodegradability_score', 'recyclability_percent', 'water_resistance', 'material_type']
        X = candidates_df[[
            'strength', 
            'weight_capacity_kg', 
            'biodegradability_score', 
            'recyclability_percent', 
            'water_resistance', 
            'material_type'
        ]]

        # 3. Generate Predictions
        # Predict Cost
        pred_cost = self.cost_model.predict(X)
        
        # Predict CO2
        pred_co2 = self.co2_model.predict(X)

        # 4. Calculate Detailed Scores
        results_df = candidates_df.copy()
        results_df['predicted_cost_inr'] = pred_cost
        results_df['predicted_co2_score'] = pred_co2

        # Normalize metrics for scoring (0 to 1 scale roughly)
        # Cost: Lower is better -> 1 / (1 + cost) match logic or min-max normalization
        # CO2: Lower is better
        
        # Simple Weighted Score
        # We want to Minimize Cost and Minimize CO2
        # Score = (w1 * Cost_Score) + (w2 * Sustainability_Score)
        # Let's retain the logic: Higher Score = Better Recommendation
        
        # Invert scales:
        # Cost Efficiency = 100 / predicted_cost (Example)
        # Eco Score = 100 / predicted_co2
        
        results_df['cost_efficiency_score'] = 100 / (results_df['predicted_cost_inr'] + 1e-5)
        results_df['eco_impact_score'] = 100 / (results_df['predicted_co2_score'] + 1e-5)
        
        # Composite Score (50% Cost, 50% Eco) - Adjustable
        results_df['final_rank_score'] = (
            0.5 * results_df['cost_efficiency_score'] + 
            0.5 * results_df['eco_impact_score']
        )

        # 5. Rank and Filter
        final_df = results_df.sort_values(by='final_rank_score', ascending=False).head(top_n)
        
        return final_df[['material_type', 'final_rank_score', 'predicted_cost_inr', 'predicted_co2_score', 'weight_capacity_kg']]

if __name__ == "__main__":
    # Test Run
    rec = MaterialRecommender()
    print("\n--- Test Recommendation for 2kg Product ---")
    recs = rec.get_recommendations(product_weight_kg=2.0, product_category="Electronics")
    print(recs)

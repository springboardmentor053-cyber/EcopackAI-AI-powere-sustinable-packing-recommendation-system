
import pandas as pd
import joblib
import os
from .db_service import db_service

class MLService:
    def __init__(self):
        self.cost_model = None
        self.co2_model = None
        self._load_models()

    def _load_models(self):
        """Load trained ML models from .pkl files."""
        try:
            # Path relative to this file: backend/app/services/ml_service.py
            # Models are in: models/
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up 3 levels to reach project root (backend/app/services -> backend/app -> backend -> root)
            model_dir = os.path.abspath(os.path.join(base_dir, '..', '..', '..', 'models'))
            
            cost_model_path = os.path.join(model_dir, 'cost_predictor_model.pkl')
            co2_model_path = os.path.join(model_dir, 'co2_predictor_model.pkl')
            
            if not os.path.exists(cost_model_path) or not os.path.exists(co2_model_path):
                print(f"⚠️ Models not found at {model_dir}")
                return

            self.cost_model = joblib.load(cost_model_path)
            self.co2_model = joblib.load(co2_model_path)
            print("✅ ML Models loaded successfully.")
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")

    def get_recommendations(self, product_weight_kg, product_category, fragility='Medium', water_resistant=False, top_n=5):
        """Recommend materials based on product constraints and ML predictions."""
        engine = db_service.get_engine()
        if engine is None:
            return pd.DataFrame()

        # 1. Fetch Candidate Materials from DB
        # Try to find materials specifically recommended for this category first
        query = f"""
        SELECT DISTINCT
            fe.material_id, 
            fe.material_type, 
            fe.strength, 
            fe.weight_capacity_kg, 
            fe.biodegradability_score, 
            fe.recyclability_percent, 
            fe.water_resistance,
            fe.manufacturing_place
        FROM features_engineering fe
        JOIN product_material pm ON fe.material_id = pm.material_id
        WHERE pm.category = '{product_category}' 
        AND fe.weight_capacity_kg >= {product_weight_kg}
        """
        
        try:
            candidates_df = pd.read_sql(query, engine)
        except Exception as e:
            print(f"❌ Error fetching candidates: {e}")
            return pd.DataFrame()

        # 1.5 Filter Initial Candidates
        candidates_filtered = candidates_df.copy()

        # Filter by Water Resistance (Initial Check)
        if water_resistant and not candidates_filtered.empty:
             candidates_filtered = candidates_filtered[candidates_filtered['water_resistance'] >= 1]

        # Filter by Fragility (Initial Check)
        if fragility == 'High' and not candidates_filtered.empty:
             candidates_filtered = candidates_filtered[candidates_filtered['strength'] >= 7]

        # If filtering reduced candidates to zero, OR if original query was empty, trigger fallback
        if candidates_filtered.empty:
            print(f"⚠️ No exact matches found for category '{product_category}' with specific constraints. Switching to broad search...")
            query_fallback = f"""
            SELECT 
                material_id, 
                material_type, 
                strength, 
                weight_capacity_kg, 
                biodegradability_score, 
                recyclability_percent, 
                water_resistance,
                manufacturing_place
            FROM features_engineering
            WHERE weight_capacity_kg >= {product_weight_kg}
            """
            try:
                candidates_df = pd.read_sql(query_fallback, engine)
            except Exception as e:
                print(f"❌ Error fetching fallback candidates: {e}")
                return pd.DataFrame()
        else:
            candidates_df = candidates_filtered

        if candidates_df.empty:
            return pd.DataFrame()
            
        # Re-apply filters to the (potentially new) fallback dataset
        if water_resistant:
            candidates_df = candidates_df[candidates_df['water_resistance'] >= 1]
            if candidates_df.empty:
                 print("⚠️ No materials found with water resistance even in broad search.")
                 return pd.DataFrame()

        if fragility == 'High':
            candidates_df = candidates_df[candidates_df['strength'] >= 7]
            if candidates_df.empty:
                 print("⚠️ No materials found with high strength even in broad search.")
                 return pd.DataFrame()

        # 2. Prepare Features for Prediction
        X = candidates_df[[
            'strength', 
            'weight_capacity_kg', 
            'biodegradability_score', 
            'recyclability_percent', 
            'water_resistance', 
            'material_type'
        ]]

        if not self.cost_model or not self.co2_model:
             print("❌ Models not loaded, cannot predict.")
             return pd.DataFrame()

        # 3. Generate Predictions
        pred_cost = self.cost_model.predict(X)
        pred_co2 = self.co2_model.predict(X)

        # 4. Calculate Scores
        results_df = candidates_df.copy()
        results_df['predicted_cost_inr'] = pred_cost
        results_df['predicted_co2_score'] = pred_co2
        
        # Scoring Logic
        results_df['cost_efficiency_score'] = 100 / (results_df['predicted_cost_inr'] + 1e-5)
        results_df['eco_impact_score'] = 100 / (results_df['predicted_co2_score'] + 1e-5)
        
        results_df['final_rank_score'] = (
            0.5 * results_df['cost_efficiency_score'] + 
            0.5 * results_df['eco_impact_score']
        )

        return results_df.sort_values(by='final_rank_score', ascending=False).head(top_n)

# Global Instance
ml_service = MLService()


import pandas as pd
import numpy as np
from .db_service import db_service

class FeatureService:
    def run_feature_engineering(self):
        """
        Reads raw data from 'materials', calculates features, and saves to 'features_engineering'.
        """
        print("⚙️ Running Feature Engineering...")
        engine = db_service.get_engine()
        
        # 1. Load Data
        query = """
        SELECT
            material_id,
            material_type,
            strength,
            weight_capacity_kg,
            biodegradability_score,
            co2_emission_score,
            recyclability_percent,
            cost_per_unit_inr,
            water_resistance,
            manufacturing_place
        FROM materials;
        """
        
        try:
            df = pd.read_sql(query, engine)
        except Exception as e:
            return {"success": False, "message": f"DB Read Error: {str(e)}"}
            
        if df.empty:
            return {"success": False, "message": "Materials table is empty."}

        # 2. Compute Features (Logic from database/feature_eng.py)
        
        # CO2 Impact Index
        df["co2_impact_index"] = df["co2_emission_score"] * df["weight_capacity_kg"]

        # Cost Efficiency Index
        df["cost_efficiency_index"] = df["strength"] / df["cost_per_unit_inr"].replace(0, np.nan)
        df["cost_efficiency_index"] = df["cost_efficiency_index"].fillna(0)

        # Sustainability Score
        df["sustainability_score"] = (
            df["biodegradability_score"] * 0.4 +
            (df["recyclability_percent"] / 100) * 0.4 -
            df["co2_emission_score"] * 0.2
        )

        # Final Suitability Score
        df["material_suitability_score"] = (
            df["cost_efficiency_index"] * 0.3 +
            df["sustainability_score"] * 0.5 +
            (df["water_resistance"] * 0.2)
        )

        # 3. Save
        try:
            df.to_sql(
                name="features_engineering",
                con=engine,
                if_exists="replace",
                index=False
            )
            print("✅ Feature engineering completed.")
            return {"success": True, "message": "Feature engineering completed."}
        except Exception as e:
             return {"success": False, "message": f"DB Write Error: {str(e)}"}

feature_service = FeatureService()

import pandas as pd
import numpy as np
import joblib
import os
import warnings
from sqlalchemy import create_engine

warnings.filterwarnings('ignore')

class EcoPackRecommender:
    
    def __init__(self):
        
        # Base project directory
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Models folder path
        model_dir = os.path.join(self.base_dir, "ml", "models")

        # Load ML models
        self.rf_suitability = joblib.load(os.path.join(model_dir, "rf_suitability.pkl"))
        self.xgb_co2 = joblib.load(os.path.join(model_dir, "xgb_co2.pkl"))
        self.rf_cost = joblib.load(os.path.join(model_dir, "rf_cost.pkl"))

        self.encoders = joblib.load(os.path.join(model_dir, "encoders.pkl"))
        self.scaler = joblib.load(os.path.join(model_dir, "scaler.pkl"))
        self.feature_columns = joblib.load(os.path.join(model_dir, "feature_columns.pkl"))

        # Load dataset
        data_path = os.path.join(self.base_dir, "data", "processed", "materials_engineered.csv")
        self.materials_df = pd.read_csv(data_path)

        # Database connection
        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:varshi123@localhost:5432/ecopackai_new"
        )

        print("Recommendation engine initialized")


    
    def _get_db_engine(self):
        return create_engine(self.db_url)
    
    def get_categories(self):
        engine = self._get_db_engine()
        query = "SELECT category_name FROM product_categories ORDER BY category_name"
        df = pd.read_sql(query, engine)
        engine.dispose()
        return df['category_name'].tolist()
    
    def get_materials(self):
        return self.materials_df['material_name'].tolist()
    
    def get_recommendations(self, category_name, product_weight_kg, top_n=5,
                            fragility_override=None, budget_limit=None):
        
        engine = self._get_db_engine()
        category_query = f"SELECT * FROM product_categories WHERE category_name = '{category_name}'"
        category_df = pd.read_sql(category_query, engine)
        engine.dispose()
        
        if len(category_df) == 0:
            raise ValueError(f"Category '{category_name}' not found")
        
        category = category_df.iloc[0]
        
        valid_fragility = ['low', 'medium', 'high']
        if fragility_override and fragility_override in valid_fragility:
            fragility_level = fragility_override
        else:
            fragility_level = category['fragility_level']
        
        predictions = []
        
        for _, material in self.materials_df.iterrows():
            features = {
                'fragility_level_encoded': self.encoders['fragility_level'].transform([fragility_level])[0],
                'requires_cushioning': int(category['requires_cushioning']),
                'moisture_sensitive': int(category['moisture_sensitive']),
                'temperature_sensitive': int(category['temperature_sensitive']),
                'product_weight_kg': product_weight_kg,
                'material_type_encoded': self.encoders['material_type'].transform([material['material_type']])[0],
                'strength_score': material['strength_score'],
                'weight_capacity_kg': material['weight_capacity_kg'],
                'biodegradability_score': material['biodegradability_score'],
                'moisture_resistance': material['moisture_resistance'],
                'co2_emission_kg': material['co2_emission_kg'],
                'cost_per_kg': material['cost_per_kg'],
                'co2_impact_index': material['co2_impact_index'],
                'cost_efficiency_index': material['cost_efficiency_index'],
                'eco_score': material['eco_score']
            }
            
            X = pd.DataFrame([features])[self.feature_columns]
            
            X_scaled = pd.DataFrame(
                self.scaler.transform(X), 
                columns=self.feature_columns
            )
            
            suitability = self.rf_suitability.predict(X_scaled)[0]
            predicted_co2 = self.xgb_co2.predict(X_scaled)[0]
            predicted_cost = self.rf_cost.predict(X_scaled)[0]
            
            can_handle_weight = material['weight_capacity_kg'] >= product_weight_kg
            
            if not can_handle_weight:
                suitability *= 0.5  
            
            predictions.append({
                'material_id': material['material_id'],
                'material_name': material['material_name'],
                'material_type': material['material_type'],
                'suitability_score': round(float(suitability), 3),
                'predicted_co2_kg': round(float(predicted_co2), 4),
                'predicted_cost_inr': round(float(predicted_cost), 2),
                'eco_score': round(float(material['eco_score']), 3),
                'biodegradability_score': round(float(material['biodegradability_score']), 2),
                'can_handle_weight': bool(can_handle_weight),
                'weight_capacity_kg': float(material['weight_capacity_kg'])
            })
        
        results_df = pd.DataFrame(predictions)
        results_df = results_df.sort_values('suitability_score', ascending=False)
        
        results_df = pd.DataFrame(predictions)
        results_df = results_df.sort_values('suitability_score', ascending=False)
        
        if budget_limit is not None:
            before_count = len(results_df)
            results_df = results_df[results_df['predicted_cost_inr'] <= budget_limit]
            filtered_count = before_count - len(results_df)
            if filtered_count > 0:
                print(f"  Budget filter: removed {filtered_count} materials exceeding Rs.{budget_limit}")
        
        if len(results_df) == 0:
            raise ValueError(f"No materials found within budget limit of Rs.{budget_limit}")
        
        return results_df.head(top_n)
    
    def compare_with_current(self, category_name, product_weight_kg, current_material_name):
        
        recommendations = self.get_recommendations(category_name, product_weight_kg, top_n=1)
        best_material = recommendations.iloc[0]
        
        current = self.materials_df[self.materials_df['material_name'] == current_material_name]
        
        if len(current) == 0:
            raise ValueError(f"Material '{current_material_name}' not found")
        
        current = current.iloc[0]
        
        packaging_factor = 0.15
        current_co2 = current['co2_emission_kg'] * product_weight_kg * packaging_factor
        current_cost = current['cost_per_kg'] * product_weight_kg * packaging_factor
        
        co2_savings = current_co2 - best_material['predicted_co2_kg']
        cost_savings = current_cost - best_material['predicted_cost_inr']
        co2_reduction_pct = (co2_savings / current_co2 * 100) if current_co2 > 0 else 0
        
        return {
            'current_material': current_material_name,
            'current_co2_kg': round(float(current_co2), 4),
            'current_cost_inr': round(float(current_cost), 2),
            'recommended_material': best_material['material_name'],
            'recommended_co2_kg': round(float(best_material['predicted_co2_kg']), 4),
            'recommended_cost_inr': round(float(best_material['predicted_cost_inr']), 2),
            'recommended_eco_score': round(float(best_material['eco_score']), 3),
            'co2_savings_kg': round(float(co2_savings), 4),
            'co2_reduction_percent': round(float(co2_reduction_pct), 1),
            'cost_difference_inr': round(float(cost_savings), 2)
        }
    
    def get_material_details(self, material_name):
        
        material = self.materials_df[self.materials_df['material_name'] == material_name]
        
        if len(material) == 0:
            raise ValueError(f"Material '{material_name}' not found")
        
        material = material.iloc[0]
        
        return {
            'material_id': int(material['material_id']),
            'material_name': material['material_name'],
            'material_type': material['material_type'],
            'strength_score': round(float(material['strength_score']), 2),
            'weight_capacity_kg': float(material['weight_capacity_kg']),
            'biodegradability_score': round(float(material['biodegradability_score']), 2),
            'co2_emission_kg': round(float(material['co2_emission_kg']), 4),
            'recyclability_percent': round(float(material['recyclability_percent']), 1),
            'cost_per_kg': round(float(material['cost_per_kg']), 2),
            'moisture_resistance': round(float(material['moisture_resistance']), 2),
            'eco_score': round(float(material['eco_score']), 3),
            'co2_impact_index': round(float(material['co2_impact_index']), 3),
            'cost_efficiency_index': round(float(material['cost_efficiency_index']), 3)
        }
        
    def save_recommendation(self, category_name, product_weight_kg, fragility_level,
                        budget_limit, current_material_name, recommendation, comparison=None):

        try:
            engine = self._get_db_engine()
            
            co2_savings = comparison['co2_savings_kg'] if comparison else None
            cost_savings = comparison['cost_difference_inr'] if comparison else None
            
            insert_query = """
                INSERT INTO recommendations (
                    category_name, product_weight_kg, fragility_level, budget_limit,
                    current_material_name, recommended_material_name, recommended_material_type,
                    suitability_score, predicted_cost_inr, predicted_co2_kg, eco_score,
                    co2_savings_kg, cost_savings_inr
                ) VALUES (
                    %(category_name)s, %(product_weight_kg)s, %(fragility_level)s, %(budget_limit)s,
                    %(current_material_name)s, %(recommended_material_name)s, %(recommended_material_type)s,
                    %(suitability_score)s, %(predicted_cost_inr)s, %(predicted_co2_kg)s, %(eco_score)s,
                    %(co2_savings_kg)s, %(cost_savings_inr)s
                )
            """
            
            params = {
                'category_name': category_name,
                'product_weight_kg': product_weight_kg,
                'fragility_level': fragility_level,
                'budget_limit': budget_limit,
                'current_material_name': current_material_name,
                'recommended_material_name': recommendation['material_name'],
                'recommended_material_type': recommendation['material_type'],
                'suitability_score': recommendation['suitability_score'],
                'predicted_cost_inr': recommendation['predicted_cost_inr'],
                'predicted_co2_kg': recommendation['predicted_co2_kg'],
                'eco_score': recommendation['eco_score'],
                'co2_savings_kg': co2_savings,
                'cost_savings_inr': cost_savings
            }
            
            with engine.connect() as conn:
                conn.execute(insert_query, params)
                conn.commit()
            
            engine.dispose()
            print(f"  Recommendation saved: {recommendation['material_name']} for {category_name}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to save recommendation: {e}")
            return False

if __name__ == "__main__":
    
    recommender = EcoPackRecommender()
import pandas as pd
import numpy as np
import joblib
import os
import warnings
from sqlalchemy import create_engine, text

warnings.filterwarnings('ignore')


class EcoPackRecommender:
        
    def __init__(self):
        """Initialize the recommendation engine with trained models and data"""
        
        # Get the base directory (project root) - works on any OS
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load trained models using relative paths
        self.rf_suitability = joblib.load(os.path.join(self.base_dir, 'ml/models/rf_suitability.pkl'))
        self.xgb_co2 = joblib.load(os.path.join(self.base_dir, 'ml/models/xgb_co2.pkl'))
        self.rf_cost = joblib.load(os.path.join(self.base_dir, 'ml/models/rf_cost.pkl'))
        
        # Load preprocessing objects
        self.encoders = joblib.load(os.path.join(self.base_dir, 'ml/models/encoders.pkl'))
        self.scaler = joblib.load(os.path.join(self.base_dir, 'ml/models/scaler.pkl'))
        self.feature_columns = joblib.load(os.path.join(self.base_dir, 'ml/models/feature_columns.pkl'))
        
        # Load materials data
        self.materials_df = pd.read_csv(os.path.join(self.base_dir, 'data/processed/materials_engineered.csv'))
        
        # Database connection
        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/ecopackai"
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
        
        # Check if recommended material is same as current material
        if best_material['material_name'] == current_material_name:
            # Same material - no savings, use consistent values
            return {
                'current_material': current_material_name,
                'current_co2_kg': round(float(best_material['predicted_co2_kg']), 4),
                'current_cost_inr': round(float(best_material['predicted_cost_inr']), 2),
                'recommended_material': best_material['material_name'],
                'recommended_co2_kg': round(float(best_material['predicted_co2_kg']), 4),
                'recommended_cost_inr': round(float(best_material['predicted_cost_inr']), 2),
                'recommended_eco_score': round(float(best_material['eco_score']), 3),
                'co2_savings_kg': 0.0,
                'co2_reduction_percent': 0.0,
                'cost_difference_inr': 0.0,
                'same_material': True
            }
        
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
            'cost_difference_inr': round(float(cost_savings), 2),
            'same_material': False
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
            
            insert_query = text("""
                INSERT INTO recommendations (
                    category_name, product_weight_kg, fragility_level, budget_limit,
                    current_material_name, recommended_material_name, recommended_material_type,
                    suitability_score, predicted_cost_inr, predicted_co2_kg, eco_score,
                    co2_savings_kg, cost_savings_inr
                ) VALUES (
                    :category_name, :product_weight_kg, :fragility_level, :budget_limit,
                    :current_material_name, :recommended_material_name, :recommended_material_type,
                    :suitability_score, :predicted_cost_inr, :predicted_co2_kg, :eco_score,
                    :co2_savings_kg, :cost_savings_inr
                )
            """)
            
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
            print(f"Recommendation saved: {recommendation['material_name']} for {category_name}")
            return True
            
        except Exception as e:
            print(f"Failed to save recommendation: {e}")
            return False
        
    def update_recommendation_with_comparison(self, category_name, product_weight_kg, comparison):
        try:
            engine = self._get_db_engine()
            
            update_query = text("""
                UPDATE recommendations
                SET current_material_name = :current_material_name,
                    co2_savings_kg = :co2_savings_kg,
                    cost_savings_inr = :cost_savings_inr
                WHERE recommendation_id = (
                    SELECT recommendation_id FROM recommendations
                    WHERE category_name = :category_name
                    AND product_weight_kg = :product_weight_kg
                    ORDER BY created_at DESC
                    LIMIT 1
                )
            """)
            
            params = {
                'category_name': category_name,
                'product_weight_kg': float(product_weight_kg),
                'current_material_name': comparison['current_material'],
                'co2_savings_kg': comparison['co2_savings_kg'],
                'cost_savings_inr': comparison['cost_difference_inr']
            }
                
            with engine.connect() as conn:
                conn.execute(update_query, params)
                conn.commit()
            
            engine.dispose()
            print(f"Updated recommendation with comparison data")
            return True
            
        except Exception as e:
            print(f"Failed to update recommendation: {e}")
            return False
        
    def get_analytics_summary(self):
        """
        Get overall analytics summary from recommendations table.
        
        Returns:
            Dictionary with total counts, CO₂ saved, cost metrics
        """
        try:
            engine = self._get_db_engine()
            
            query = text("""
                SELECT 
                    COUNT(*) as total_recommendations,
                    COUNT(DISTINCT category_name) as categories_served,
                    COUNT(DISTINCT recommended_material_name) as unique_materials_recommended,
                    COALESCE(SUM(co2_savings_kg), 0) as total_co2_saved_kg,
                    COALESCE(SUM(cost_savings_inr), 0) as total_cost_saved_inr,
                    COALESCE(AVG(predicted_co2_kg), 0) as avg_co2_per_recommendation,
                    COALESCE(AVG(predicted_cost_inr), 0) as avg_cost_per_recommendation,
                    COALESCE(AVG(suitability_score), 0) as avg_suitability_score,
                    COALESCE(AVG(eco_score), 0) as avg_eco_score,
                    COUNT(CASE WHEN co2_savings_kg > 0 THEN 1 END) as recommendations_with_savings,
                    MIN(created_at) as first_recommendation,
                    MAX(created_at) as last_recommendation
                FROM recommendations
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query)
                row = result.fetchone()
            
            engine.dispose()
            
            if row is None or row[0] == 0:
                return {
                    'total_recommendations': 0,
                    'categories_served': 0,
                    'unique_materials_recommended': 0,
                    'total_co2_saved_kg': 0,
                    'total_cost_saved_inr': 0,
                    'avg_co2_per_recommendation': 0,
                    'avg_cost_per_recommendation': 0,
                    'avg_suitability_score': 0,
                    'avg_eco_score': 0,
                    'recommendations_with_savings': 0,
                    'first_recommendation': None,
                    'last_recommendation': None
                }
            
            return {
                'total_recommendations': int(row[0]),
                'categories_served': int(row[1]),
                'unique_materials_recommended': int(row[2]),
                'total_co2_saved_kg': round(float(row[3]), 4),
                'total_cost_saved_inr': round(float(row[4]), 2),
                'avg_co2_per_recommendation': round(float(row[5]), 4),
                'avg_cost_per_recommendation': round(float(row[6]), 2),
                'avg_suitability_score': round(float(row[7]), 3),
                'avg_eco_score': round(float(row[8]), 3),
                'recommendations_with_savings': int(row[9]),
                'first_recommendation': row[10].isoformat() if row[10] else None,
                'last_recommendation': row[11].isoformat() if row[11] else None
            }
            
        except Exception as e:
            print(f"Failed to get analytics summary: {e}")
            return None


    def get_analytics_by_material(self, limit=10):
        """
        Get recommendation counts grouped by material.
        
        Args:
            limit: Number of top materials to return (default 10)
        
        Returns:
            List of dictionaries with material stats
        """
        try:
            engine = self._get_db_engine()
            
            query = text("""
                SELECT 
                    recommended_material_name,
                    recommended_material_type,
                    COUNT(*) as recommendation_count,
                    COALESCE(AVG(suitability_score), 0) as avg_suitability,
                    COALESCE(AVG(predicted_co2_kg), 0) as avg_co2_kg,
                    COALESCE(AVG(predicted_cost_inr), 0) as avg_cost_inr,
                    COALESCE(AVG(eco_score), 0) as avg_eco_score
                FROM recommendations
                GROUP BY recommended_material_name, recommended_material_type
                ORDER BY recommendation_count DESC
                LIMIT :limit
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query, {'limit': limit})
                rows = result.fetchall()
            
            engine.dispose()
            
            materials = []
            for row in rows:
                materials.append({
                    'material_name': row[0],
                    'material_type': row[1],
                    'recommendation_count': int(row[2]),
                    'avg_suitability': round(float(row[3]), 3),
                    'avg_co2_kg': round(float(row[4]), 4),
                    'avg_cost_inr': round(float(row[5]), 2),
                    'avg_eco_score': round(float(row[6]), 3)
                })
            
            return materials
            
        except Exception as e:
            print(f"Failed to get material analytics: {e}")
            return []


    def get_analytics_by_category(self):
        """
        Get recommendation stats grouped by product category.
        
        Returns:
            List of dictionaries with category stats
        """
        try:
            engine = self._get_db_engine()
            
            query = text("""
                SELECT 
                    category_name,
                    COUNT(*) as recommendation_count,
                    COALESCE(SUM(co2_savings_kg), 0) as total_co2_saved,
                    COALESCE(SUM(cost_savings_inr), 0) as total_cost_saved,
                    COALESCE(AVG(predicted_co2_kg), 0) as avg_co2_kg,
                    COALESCE(AVG(predicted_cost_inr), 0) as avg_cost_inr,
                    COALESCE(AVG(suitability_score), 0) as avg_suitability
                FROM recommendations
                GROUP BY category_name
                ORDER BY recommendation_count DESC
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
            
            engine.dispose()
            
            categories = []
            for row in rows:
                categories.append({
                    'category_name': row[0],
                    'recommendation_count': int(row[1]),
                    'total_co2_saved': round(float(row[2]), 4),
                    'total_cost_saved': round(float(row[3]), 2),
                    'avg_co2_kg': round(float(row[4]), 4),
                    'avg_cost_inr': round(float(row[5]), 2),
                    'avg_suitability': round(float(row[6]), 3)
                })
            
            return categories
            
        except Exception as e:
            print(f"Failed to get category analytics: {e}")
            return []
        
    def get_recent_recommendations(self, limit=10):
        """
        Get most recent recommendations.
        
        Args:
            limit: Number of recent records to return (default 10)
        
        Returns:
            List of recent recommendation dictionaries
        """
        try:
            engine = self._get_db_engine()
            
            query = text("""
                SELECT 
                    recommendation_id,
                    category_name,
                    product_weight_kg,
                    recommended_material_name,
                    suitability_score,
                    predicted_cost_inr,
                    predicted_co2_kg,
                    eco_score,
                    co2_savings_kg,
                    cost_savings_inr,
                    created_at
                FROM recommendations
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query, {'limit': limit})
                rows = result.fetchall()
            
            engine.dispose()
            
            recommendations = []
            for row in rows:
                recommendations.append({
                    'id': int(row[0]),
                    'category': row[1],
                    'weight_kg': float(row[2]),
                    'material': row[3],
                    'suitability': round(float(row[4]), 3) if row[4] else 0,
                    'cost_inr': round(float(row[5]), 2) if row[5] else 0,
                    'co2_kg': round(float(row[6]), 4) if row[6] else 0,
                    'eco_score': round(float(row[7]), 3) if row[7] else 0,
                    'co2_saved': round(float(row[8]), 4) if row[8] else None,
                    'cost_saved': round(float(row[9]), 2) if row[9] else None,
                    'timestamp': row[10].strftime('%Y-%m-%d %H:%M') if row[10] else None
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Failed to get recent recommendations: {e}")
            return []

if __name__ == "__main__":
    
    recommender = EcoPackRecommender()
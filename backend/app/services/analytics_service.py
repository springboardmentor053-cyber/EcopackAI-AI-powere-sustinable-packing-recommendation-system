
import pandas as pd
from .db_service import db_service

class AnalyticsService:
    def get_avg_co2_by_material(self):
        engine = db_service.get_engine()
        query = """
        SELECT material_type, AVG(co2_emission_score) as avg_co2
        FROM features_engineering
        GROUP BY material_type
        ORDER BY avg_co2 ASC;
        """
        try:
            return pd.read_sql(query, engine)
        except Exception as e:
            print(f"Error fetching CO2 stats: {e}")
            return pd.DataFrame()

    def get_sustainability_distribution(self):
        engine = db_service.get_engine()
        query = "SELECT sustainability_score FROM features_engineering;"
        try:
            return pd.read_sql(query, engine)
        except Exception as e:
            print(f"Error fetching sustainability scores: {e}")
            return pd.DataFrame()

    def get_material_category_counts(self):
        engine = db_service.get_engine()
        query = """
        SELECT category, COUNT(material_id) as material_count
        FROM product_material
        GROUP BY category
        ORDER BY material_count DESC;
        """
        try:
            return pd.read_sql(query, engine)
        except Exception as e:
            print(f"Error fetching category counts: {e}")
            return pd.DataFrame()

    def get_cost_distribution(self):
        engine = db_service.get_engine()
        query = """
        SELECT material_type, cost_per_unit_inr
        FROM features_engineering
        ORDER BY cost_per_unit_inr ASC;
        """
        try:
            return pd.read_sql(query, engine)
        except Exception as e:
             print(f"Error fetching cost stats: {e}")
             return pd.DataFrame()

    
    def get_summary_kpis(self):
        engine = db_service.get_engine()
        try:
             # Calculate simplified KPIs from existing data
             query = """
             SELECT 
                AVG(co2_emission_score) as avg_co2,
                MAX(co2_emission_score) as max_co2,
                AVG(cost_per_unit_inr) as avg_cost,
                MAX(cost_per_unit_inr) as max_cost
             FROM features_engineering
             """
             stats = pd.read_sql(query, engine).iloc[0]
             
             # Best Material
             best_mat_query = """
             SELECT material_type FROM features_engineering ORDER BY co2_emission_score ASC LIMIT 1
             """
             best_mat = pd.read_sql(best_mat_query, engine).iloc[0]['material_type']

             return {
                 "avg_co2_reduction": round(((stats['max_co2'] - stats['avg_co2']) / stats['max_co2']) * 100, 1),
                 "avg_cost_savings": round(((stats['max_cost'] - stats['avg_cost']) / stats['max_cost']) * 100, 1),
                 "best_eco_material": best_mat,
                 "total_materials": 0 # Placeholder if needed, or fetched separately
             }
        except Exception as e:
            print(f"Error fetching KPIs: {e}")
            return {
                "avg_co2_reduction": 0,
                "avg_cost_savings": 0,
                "best_eco_material": "N/A"
            }

analytics_service = AnalyticsService()

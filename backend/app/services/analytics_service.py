
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

analytics_service = AnalyticsService()

from sqlalchemy import create_engine
from src.utils.config import settings

engine = create_engine(settings.DATABASE_URL)

def fetch_materials():
    query = """
        SELECT
            material_id,
            material_type,
            material_category,
            strength_level,
            weight_capacity,
            biodegradability_score,
            recyclability_pct,
            co2_emission_kg_per_kg,
            cost_inr_per_kg
        FROM materials;
    """
    return query

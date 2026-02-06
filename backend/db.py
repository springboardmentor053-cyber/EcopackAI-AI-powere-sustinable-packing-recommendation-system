import os
import psycopg2
import pandas as pd


def get_conn():
    """
    Returns a PostgreSQL connection using environment variables.
    Keeps your defaults but adds clearer failure messages.
    """
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "ecopackai_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "042006"),
        )
    except Exception as e:
        raise RuntimeError(
            "Failed to connect to PostgreSQL. Check DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD."
        ) from e


def load_materials():
    query = """
        SELECT material_id, material_name, strength_score, weight_capacity_kg,
               biodegradability_score, co2_emission_kg, recyclability_percent,
               cost_per_unit_inr, product_category, used_for_products
        FROM public.materials;
    """
    with get_conn() as conn:
        df = pd.read_sql_query(query, conn)
    return df


def load_products():
    query = """
        SELECT product_id, product_name, product_category, product_weight_kg,
               fragility_level, required_strength_score, preferred_biodegradability_score,
               max_packaging_cost_inr, temperature_sensitive
        FROM public.products;
    """
    with get_conn() as conn:
        df = pd.read_sql_query(query, conn)
    return df

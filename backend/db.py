import os
import psycopg2
import pandas as pd


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "ecopackai_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "042006"),
    )


def load_materials():
    query = """
        SELECT material_id, material_name, strength_score, weight_capacity_kg,
               biodegradability_score, co2_emission_kg, recyclability_percent,
               cost_per_unit_inr, product_category, used_for_products
        FROM public.materials;
    """
    with get_conn() as conn:
        return pd.read_sql_query(query, conn)


def load_products():
    query = """
        SELECT product_id, product_name, product_category, product_weight_kg,
               fragility_level, required_strength_score, preferred_biodegradability_score,
               max_packaging_cost_inr, temperature_sensitive
        FROM public.products;
    """
    with get_conn() as conn:
        return pd.read_sql_query(query, conn)

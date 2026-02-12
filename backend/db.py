import os
import psycopg2
import pandas as pd


# -------------------------------------------------------------------
# Database Connection
# -------------------------------------------------------------------

def get_conn():
    """
    Returns a PostgreSQL connection.

    Priority:
    1) Uses DATABASE_URL (for Render / production)
    2) Falls back to individual DB_* environment variables (local dev)
    """

    db_url = os.getenv("DATABASE_URL")

    try:
        if db_url:
            # Fix for providers that use postgres:// instead of postgresql://
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)

            return psycopg2.connect(db_url)

        # Local fallback
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "ecopackai_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
        )

    except Exception as e:
        raise RuntimeError(
            "Failed to connect to PostgreSQL.\n"
            "If deployed: check DATABASE_URL.\n"
            "If local: check DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD."
        ) from e


# -------------------------------------------------------------------
# Core Data Loaders (Materials & Products)
# -------------------------------------------------------------------

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
               fragility_level, required_strength_score,
               preferred_biodegradability_score,
               max_packaging_cost_inr, temperature_sensitive
        FROM public.products;
    """
    with get_conn() as conn:
        df = pd.read_sql_query(query, conn)
    return df


# -------------------------------------------------------------------
# Recommendation Logging (Module 7 - BI Dashboard)
# -------------------------------------------------------------------

def insert_recommendation_log(
    product_category=None,
    product_weight_kg=None,
    fragility=None,
    recommended_material=None,
    predicted_cost=None,
    predicted_co2=None
):
    """
    Inserts one recommendation record into recommendation_logs table.
    Safe even if some values are None.
    """

    sql = """
        INSERT INTO public.recommendation_logs
        (product_category, product_weight_kg, fragility,
         recommended_material, predicted_cost, predicted_co2)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                product_category,
                product_weight_kg,
                fragility,
                recommended_material,
                predicted_cost,
                predicted_co2
            ))
        conn.commit()


# -------------------------------------------------------------------
# Dashboard Aggregations
# -------------------------------------------------------------------

def fetch_dashboard_summary(include_raw=False):
    """
    Returns dashboard summary metrics:
    - total requests
    - average cost
    - average CO2
    - top recommended materials
    - category-level averages
    - optional raw logs
    """

    with get_conn() as conn:
        cursor = conn.cursor()

        # Total recommendations
        cursor.execute("SELECT COUNT(*) FROM recommendation_logs;")
        total_requests = cursor.fetchone()[0]

        # Avg cost + CO2
        cursor.execute("""
            SELECT AVG(predicted_cost), AVG(predicted_co2)
            FROM recommendation_logs;
        """)
        avg_row = cursor.fetchone()
        avg_cost = avg_row[0] or 0
        avg_co2 = avg_row[1] or 0

        # Top materials
        cursor.execute("""
            SELECT recommended_material, COUNT(*) AS cnt
            FROM recommendation_logs
            GROUP BY recommended_material
            ORDER BY cnt DESC
            LIMIT 5;
        """)
        top_materials = [
            {"recommended_material": r[0], "cnt": r[1]}
            for r in cursor.fetchall()
        ]

        # Category averages
        cursor.execute("""
            SELECT product_category,
                   AVG(predicted_cost) AS avg_cost,
                   AVG(predicted_co2) AS avg_co2,
                   COUNT(*) AS cnt
            FROM recommendation_logs
            GROUP BY product_category
            ORDER BY cnt DESC;
        """)
        by_category = [
            {
                "product_category": r[0],
                "avg_cost": r[1],
                "avg_co2": r[2],
                "cnt": r[3],
            }
            for r in cursor.fetchall()
        ]

        # Raw logs (optional)
        raw_logs = []
        if include_raw:
            cursor.execute("""
                SELECT id, created_at, product_category,
                       product_weight_kg, fragility,
                       recommended_material, predicted_cost, predicted_co2
                FROM recommendation_logs
                ORDER BY created_at DESC
                LIMIT 500;
            """)
            raw_logs = [
                {
                    "id": r[0],
                    "created_at": r[1],
                    "product_category": r[2],
                    "product_weight_kg": r[3],
                    "fragility": r[4],
                    "recommended_material": r[5],
                    "predicted_cost": r[6],
                    "predicted_co2": r[7],
                }
                for r in cursor.fetchall()
            ]

    return {
        "total_requests": total_requests,
        "avg_cost": avg_cost,
        "avg_co2": avg_co2,
        "top_materials": top_materials,
        "by_category": by_category,
        "raw_logs": raw_logs,
    }


# -------------------------------------------------------------------
# Data Export Helper
# -------------------------------------------------------------------

def fetch_logs_df(limit=500):
    """
    Returns latest recommendation logs as a pandas DataFrame.
    Useful for Excel export or reporting.
    """

    query = f"""
        SELECT id, created_at, product_category, product_weight_kg, fragility,
               recommended_material, predicted_cost, predicted_co2
        FROM recommendation_logs
        ORDER BY created_at DESC
        LIMIT {int(limit)};
    """

    with get_conn() as conn:
        df = pd.read_sql_query(query, conn)

    return df

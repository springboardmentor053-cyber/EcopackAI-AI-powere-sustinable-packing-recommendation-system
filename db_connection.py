from sqlalchemy import create_engine, text
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

def create_tables(engine):
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS materials (
            material_id INT PRIMARY KEY,
            material_type VARCHAR(100),
            strength FLOAT,
            weight_capacity FLOAT,
            cost_per_unit FLOAT,
            biodegradability_score FLOAT,
            co2_emission_score FLOAT,
            recyclability_percentage FLOAT,
            product_category VARCHAR(50)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(100),
            product_category VARCHAR(50),
            fragility_level VARCHAR(20),
            shipping_type VARCHAR(20)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS material_product_scores (
            score_id INT PRIMARY KEY,
            material_id INT REFERENCES materials(material_id),
            product_id INT REFERENCES products(product_id),
            material_sustainability_score FLOAT,
            co2_impact_index FLOAT,
            cost_efficiency_index FLOAT
        );
        """))



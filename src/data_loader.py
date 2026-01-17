import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("data/processed/ecopackai_feature_engineered.csv")
print("Loaded dataset shape:", df.shape)

engine = create_engine(
    "postgresql+psycopg2://postgres:admin@localhost:5432/ecopackai"
)

materials_df = df[
    [
        "material_type",
        "strength",
        "weight_capacity",
        "cost_per_unit",
        "biodegradability_score",
        "recyclability_percentage",
    ]
].drop_duplicates(subset=["material_type"])

materials_df.to_sql(
    "materials",
    engine,
    if_exists="append",
    index=False
)

print("Materials table populated")
products_df = df[
    [
        "product_category",
        "fragility_level",
        "shipping_type",
    ]
].drop_duplicates(
    subset=["product_category", "fragility_level", "shipping_type"]
)

products_df.to_sql(
    "products",
    engine,
    if_exists="append",
    index=False
)

print("Products table populated")

materials_db = pd.read_sql(
    "SELECT material_id, material_type FROM materials",
    engine
)

products_db = pd.read_sql(
    "SELECT product_id, product_category, fragility_level, shipping_type FROM products",
    engine
)

df_scores = df.merge(
    materials_db,
    on="material_type",
    how="left"
)

df_scores = df_scores.merge(
    products_db,
    on=["product_category", "fragility_level", "shipping_type"],
    how="left"
)

scores_df = df_scores[
    [
        "material_id",
        "product_id",
        "material_suitability_score",
        "co2_impact_index",
        "cost_efficiency_index",
    ]
]

scores_df.to_sql(
    "material_product_scores",
    engine,
    if_exists="append",
    index=False
)

print("Material–product scores populated")
print("Total score rows inserted:", len(scores_df))


import psycopg2
conn = psycopg2.connect(
 dbname="ecopackai",
user="postgres",
 password="YOUR_PASSWORD",
host="localhost",
port="5432"
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM materials;")
print(cur.fetchone())
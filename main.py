import os
from data_generation import generate_datasets
from data_cleaning import clean_materials
from feature_engineering import normalize, encode_materials, generate_scores
from db_connection import get_engine, create_tables

print(" main.py started")

# Create data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_folder = os.path.join(project_root, "data")
os.makedirs(data_folder, exist_ok=True)

print(" Generating datasets...")
df_materials, df_products = generate_datasets()

print(" Cleaning data...")
df_materials = clean_materials(df_materials)

num_cols = ['strength', 'weight_capacity', 'cost_per_unit',
            'biodegradability_score', 'co2_emission_score', 'recyclability_percentage']

print(" Normalizing numeric columns...")
df_materials = normalize(df_materials, num_cols)

print(" Encoding categorical features...")
df_materials_encoded = encode_materials(df_materials)

print(" Feature engineering scores...")
df_scores = generate_scores(df_materials, df_products)

print(" Saving CSV files...")
df_materials.to_csv(os.path.join(data_folder, "materials_80rows.csv"), index=False)
df_products.to_csv(os.path.join(data_folder, "products_80rows.csv"), index=False)
df_materials_encoded.to_csv(os.path.join(data_folder, "materials_processed_80rows.csv"), index=False)
df_scores.to_csv(os.path.join(data_folder, "material_product_scores_80rows.csv"), index=False)

print(" Connecting to PostgreSQL...")
engine = get_engine()
create_tables(engine)

print(" Inserting data into PostgreSQL...")
df_materials.to_sql('materials', engine, if_exists='replace', index=False)
df_products.to_sql('products', engine, if_exists='replace', index=False)
df_scores.to_sql('material_product_scores', engine, if_exists='replace', index=False)

print(" main.py finished successfully")


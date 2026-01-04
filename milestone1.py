# milestone1.py

import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text

# -----------------------------
# Step 0: Create 'data' folder at project root
# -----------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_folder = os.path.join(project_root, "data")

if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# -----------------------------
# Step 1: Generate Materials Dataset (80 rows)
# -----------------------------
np.random.seed(42)

material_types = [
    "Corrugated Cardboard", "Molded Pulp", "Biodegradable Plastic",
    "Recycled Paper", "Plant Fiber", "Starch-based Plastic"
]

product_categories = ["Electronics", "Food", "Cosmetics", "Clothing", "Furniture"]

materials_data = {
    "material_id": np.arange(1, 81, dtype=int),
    "material_type": np.random.choice(material_types, 80),
    "strength": np.round(np.random.uniform(5, 10, 80), 2).astype(float),
    "weight_capacity": np.round(np.random.uniform(5, 25, 80), 2).astype(float),
    "cost_per_unit": np.round(np.random.uniform(10, 50, 80), 2).astype(float),
    "biodegradability_score": np.round(np.random.uniform(5, 10, 80), 2).astype(float),
    "co2_emission_score": np.round(np.random.uniform(1, 5, 80), 2).astype(float),
    "recyclability_percentage": np.round(np.random.uniform(50, 100, 80), 2).astype(float),
    "product_category": np.random.choice(product_categories, 80)
}

df_materials = pd.DataFrame(materials_data)

# Introduce some missing values for demonstration
df_materials.loc[0, 'strength'] = np.nan
df_materials.loc[1, 'co2_emission_score'] = np.nan

# -----------------------------
# Step 2: Generate Products Dataset (80 rows)
# -----------------------------
fragility_levels = ["Low", "Medium", "High"]
shipping_types = ["Air", "Sea", "Road"]

products_data = {
    "product_id": np.arange(1, 81, dtype=int),
    "product_name": ["Product_" + str(i) for i in range(1, 81)],
    "product_category": np.random.choice(product_categories, 80),
    "fragility_level": np.random.choice(fragility_levels, 80),
    "shipping_type": np.random.choice(shipping_types, 80)
}

df_products = pd.DataFrame(products_data)

# -----------------------------
# Step 3: Handle missing values
# -----------------------------
df_materials.fillna(0, inplace=True)  # show missing values replaced with 0

# -----------------------------
# Step 4: Normalize numeric features
# -----------------------------
num_cols = ['strength', 'weight_capacity', 'cost_per_unit',
            'biodegradability_score', 'co2_emission_score', 'recyclability_percentage']

df_materials[num_cols] = (df_materials[num_cols] - df_materials[num_cols].min()) / (df_materials[num_cols].max() - df_materials[num_cols].min())

# -----------------------------
# Step 5: Encode categorical material properties
# -----------------------------
df_materials_encoded = pd.get_dummies(df_materials, columns=['material_type', 'product_category'])

# -----------------------------
# Step 6: Feature engineering for material_product_scores
# -----------------------------
df_scores = pd.DataFrame()
df_scores['score_id'] = np.arange(1, 81, dtype=int)
df_scores['material_id'] = df_materials['material_id']
df_scores['product_id'] = df_products['product_id']
df_scores['material_sustainability_score'] = df_materials['biodegradability_score'] * df_materials['recyclability_percentage']
df_scores['co2_impact_index'] = df_materials['co2_emission_score'] * df_materials['weight_capacity']
df_scores['cost_efficiency_index'] = df_materials['strength'] / (df_materials['weight_capacity'] + 1)

# -----------------------------
# Step 7: Print outputs
# -----------------------------
print("\n✅ Materials Dataset (first 10 rows):")
print(df_materials.head(10))

print("\n✅ Products Dataset (first 10 rows):")
print(df_products.head(10))

print("\n✅ Material_Product_Scores Dataset (first 10 rows):")
print(df_scores.head(10))

# Missing values report
print("\n--- Missing Values Report ---")
print(df_materials.isna().sum())

# Summary statistics
print("\n--- Summary Statistics for Materials ---")
print(df_materials.describe())

print("\n--- Summary Statistics for Scores ---")
print(df_scores.describe())

# -----------------------------
# Step 8: Save CSVs in data folder
# -----------------------------
df_materials.to_csv(os.path.join(data_folder, "materials_80rows.csv"), index=False)
df_products.to_csv(os.path.join(data_folder, "products_80rows.csv"), index=False)
df_materials_encoded.to_csv(os.path.join(data_folder, "materials_processed_80rows.csv"), index=False)
df_scores.to_csv(os.path.join(data_folder, "material_product_scores_80rows.csv"), index=False)

print("\n✅ CSV files saved locally under 'data/' folder.")

# -----------------------------
# Step 9: PostgreSQL Setup and Insert Data
# -----------------------------
user = "postgres"
password = "Rani1234"
host = "localhost"
port = "5432"
database = "ecopackai"

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

with engine.connect() as conn:
    # Create materials table
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

    # Create products table
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INT PRIMARY KEY,
        product_name VARCHAR(100),
        product_category VARCHAR(50),
        fragility_level VARCHAR(20),
        shipping_type VARCHAR(20)
    );
    """))

    # Create material_product_scores table
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

# Insert data into PostgreSQL
df_materials.to_sql('materials', engine, if_exists='replace', index=False)
df_products.to_sql('products', engine, if_exists='replace', index=False)
df_scores.to_sql('material_product_scores', engine, if_exists='replace', index=False)

print("\n✅ Data inserted successfully into PostgreSQL tables: materials, products & material_product_scores")


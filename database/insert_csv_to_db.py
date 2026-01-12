import os
import pandas as pd
import psycopg2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "echo_pack",
    "user": "postgres",
    "password": "123456"
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
print("Connected to database")

for file in os.listdir(PROCESSED_DIR):
    if not file.endswith(".csv"):
        continue

    file_path = os.path.join(PROCESSED_DIR, file)
    df = pd.read_csv(file_path)

    print(f"Inserting {file} ...")

    if file == "cleaned_material_data.csv":
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO raw.materials_data (
                    material_id,
                    material_type,
                    strength,
                    weight_capacity_kg,
                    biodegradability_score,
                    co2_emission_score,
                    recyclability_percent,
                    cost_per_unit_inr,
                    water_resistance,
                    recycle_time_days,
                    manufacturing_place
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (material_id) DO NOTHING
            """, tuple(row))

    else:
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO raw.product_material_map (
                    material_id,
                    eco_alternative,
                    category,
                    product_domain
                ) VALUES (%s,%s,%s,%s)
            """, tuple(row))

    print(f"{file} inserted successfully")

conn.commit()
cursor.close()
conn.close()

print("All processed files inserted successfully")

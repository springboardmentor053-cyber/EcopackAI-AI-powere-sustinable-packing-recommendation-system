import os
import pandas as pd
import psycopg2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "feature_engineered_materials.csv"
)

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="echo_pack",
    user="postgres",
    password="123456"
)

cursor = conn.cursor()
print("Connected to database")

df = pd.read_csv(CSV_PATH)

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO ml.material_features (
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
            manufacturing_place,
            co2_impact_index,
            cost_efficiency_index,
            material_suitability_score
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (material_id) DO NOTHING
    """, tuple(row))

conn.commit()
cursor.close()
conn.close()

print("ML feature data inserted successfully")

import psycopg2
import pandas as pd


df = pd.read_csv("data/processed/cleaned_material_data.csv")

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="eco_packaging",
    user="postgres",
    password="123456"
)

cursor = conn.cursor()

df = pd.read_csv("data/processed/feature_engineered_materials.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO public.feature_engineered_materials (
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
print("feature_engineered_materials inserted")



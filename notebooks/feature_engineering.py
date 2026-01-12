import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

input_file = os.path.join(PROCESSED_DIR, "cleaned_material_data.csv")
output_file = os.path.join(PROCESSED_DIR, "feature_engineered_materials.csv")

df = pd.read_csv(input_file)

df["co2_impact_index"] = df["co2_emission_score"] * df["weight_capacity_kg"]

df["cost_efficiency_index"] = (
    df["weight_capacity_kg"] / df["cost_per_unit_inr"]
)

df["material_suitability_score"] = (
    df["biodegradability_score"] * 0.4 +
    df["recyclability_percent"] * 0.3 +
    df["cost_efficiency_index"] * 0.3
)

df.to_csv(output_file, index=False)

print("Feature engineering completed successfully")

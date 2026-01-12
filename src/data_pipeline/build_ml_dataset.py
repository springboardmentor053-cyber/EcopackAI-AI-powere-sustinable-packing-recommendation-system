import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PRODUCT_DATA = BASE_DIR / "data" / "final" / "ml_dataset.csv"
MATERIAL_DATA = BASE_DIR / "data" /"processed" / "cleaned_material_data.csv"
OUTPUT_PATH = BASE_DIR / "data" / "final" / "ml_dataset_with_sustainability_score.csv"

def build_ml_dataset():
    products = pd.read_csv(PRODUCT_DATA)
    materials = pd.read_csv(MATERIAL_DATA)

    df = products.merge(materials, on="material_id", how="left")

    # 🔧 Handle missing values
    df["biodegradability_score"] = df["biodegradability_score"].fillna(df["biodegradability_score"].mean())
    df["recyclability_percent"] = df["recyclability_percent"].fillna(df["recyclability_percent"].mean())
    df["co2_emission_score"] = df["co2_emission_score"].replace(0, np.nan)
    df["co2_emission_score"] = df["co2_emission_score"].fillna(df["co2_emission_score"].mean())

    # 🔢 Normalize recyclability (0–1)
    df["recyclability_norm"] = df["recyclability_percent"] / 100

    # 🌱 Sustainability Score
    df["sustainability_score"] = (
        0.4 * df["biodegradability_score"] +
        0.3 * df["recyclability_norm"] +
        0.3 * (1 / df["co2_emission_score"])
    )

    # Cleanup
    df = df.drop(columns=["material_id", "recyclability_norm"])

    df.to_csv(OUTPUT_PATH, index=False)
    print("Sustainability score computed successfully")

if __name__ == "__main__":
    build_ml_dataset()

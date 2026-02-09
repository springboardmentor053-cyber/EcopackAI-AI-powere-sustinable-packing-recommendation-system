import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "materials_ml_ready.csv")

df = pd.read_csv(DATA_PATH)

def recommend_materials(category, weight, fragility, budget, eco_priority, top_n):

    # Column for category
    col_name = f"product_category_{category}"

    filtered = df.copy()

    # Filter by product category if exists
    if col_name in filtered.columns:
        filtered = filtered[filtered[col_name] == 1]

    # Scale cost & CO2 by weight
    filtered["final_cost"] = (filtered["pred_cost"] * weight).round(2)
    filtered["final_co2"] = (filtered["pred_co2"] * weight).round(3)

    # Remove negative CO2 (safety)
    filtered["final_co2"] = filtered["final_co2"].clip(lower=0.01)

    # Budget filtering
    primary = filtered[filtered["final_cost"] <= budget]
    fallback = filtered[filtered["final_cost"] > budget]

    # Ranking score
    primary = primary.sort_values(
        "material_suitability_score", ascending=False
    )

    fallback = fallback.sort_values(
        "material_suitability_score", ascending=False
    )

    final = pd.concat([primary, fallback]).head(top_n)

    return final[[
        "material_name",
        "material_suitability_score",
        "final_cost",
        "final_co2"
    ]].rename(columns={
        "material_name": "material",
        "material_suitability_score": "suitability",
        "final_cost": "cost",
        "final_co2": "co2"
    }).to_dict(orient="records")

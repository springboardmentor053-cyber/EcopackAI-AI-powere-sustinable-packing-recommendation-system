import pandas as pd
import os

# Load dataset correctly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "materials_ml_ready.csv")

df = pd.read_csv(DATA_PATH)


def recommend_materials(product_category, weight, fragility, budget, eco_priority, recommendations):

    df_copy = df.copy()

    # -------- 1. Category Filter --------
    category_column = f"product_category_{product_category}"

    if category_column in df_copy.columns:
        df_copy = df_copy[df_copy[category_column] == 1]

    # If empty, fallback
    if df_copy.empty:
        df_copy = df.copy()

    # -------- 2. Budget Filter --------
    # Assume cost_per_unit scaled 0–1 → convert to ₹
    df_copy["real_cost"] = df_copy["cost_per_unit"] * 100

    df_copy = df_copy[df_copy["real_cost"] <= budget]

    if df_copy.empty:
        df_copy = df.copy()

    # -------- 3. Eco Weight --------
    eco_weight_map = {
        "Low": 0.2,
        "Medium": 0.4,
        "High": 0.6
    }

    eco_weight = eco_weight_map.get(eco_priority, 0.4)

    # -------- 4. Fragility Impact --------
    fragility_map = {
        "Low": 0.1,
        "Medium": 0.2,
        "High": 0.3
    }

    protection_score = fragility_map.get(fragility, 0.2)

    # -------- 5. Final Score --------
    df_copy["final_score"] = (
        (df_copy["biodegradability_score"] * eco_weight) +
        (df_copy["recyclability_percentage"] * 0.3) +
        ((1 - df_copy["co2_emission_score"]) * 0.2) +
        protection_score
    )

    df_copy = df_copy.sort_values(by="final_score", ascending=False)

    top = df_copy.head(recommendations)

    results = []

    for _, row in top.iterrows():
        results.append({
            "Material": int(row["material_id"]),
            "final_cost": round(row["real_cost"], 2),
            "final_co2": round(row["co2_emission_score"] * 100, 2),
            "cost_savings_percent": round((1 - row["cost_per_unit"]) * 100, 2),
            "co2_reduction_percent": round((1 - row["co2_emission_score"]) * 100, 2)
        })

    return results

import pandas as pd

STRENGTH_MAP = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

def rank_materials(materials_df, product, co2_model, cost_model, top_k=3):
    df = materials_df.copy()


    required_strength = STRENGTH_MAP[product["strength_level"]]
    product_weight_kg = float(product["product_weight_g"]) / 1000.0
    user_bio = float(product["biodegradability_score"])       
    user_recy = float(product["recyclability_pct"])         


    if "strength_encoded" not in df.columns:
        if "strength_level" not in df.columns:
            raise KeyError("materials_df missing both 'strength_encoded' and 'strength_level'")
        df["strength_encoded"] = df["strength_level"].map(STRENGTH_MAP)


    filtered = df[
        (df["strength_encoded"] >= required_strength) &
        (df["weight_capacity"] >= product_weight_kg * 0.7)  
    ]

 
    if filtered.empty:
        filtered = df.copy()
        

    if "cost_efficiency_index" not in filtered.columns:
        raise KeyError("cost_efficiency_index missing from materials data")



    feature_cols = [
        "strength_encoded",
        "weight_capacity",
        "biodegradability_score",
        "recyclability_pct",
        "cost_efficiency_index"
    ]


    X = filtered[feature_cols]

    filtered["predicted_cost_inr_per_kg"] = cost_model.predict(X)
    filtered["predicted_co2_impact"] = co2_model.predict(X)


    def normalize(s):
        return (s - s.min()) / (s.max() - s.min() + 1e-6)

    filtered["cost_score"] = 1 - normalize(filtered["predicted_cost_inr_per_kg"])
    filtered["co2_score"] = 1 - normalize(filtered["predicted_co2_impact"])

    filtered["bio_penalty"] = (filtered["biodegradability_score"] - user_bio).abs() / 10.0
    filtered["recy_penalty"] = (filtered["recyclability_pct"] - user_recy).abs() / 100.0


    filtered["final_score"] = (
        0.30 * filtered["cost_score"] +
        0.30 * filtered["co2_score"] +
        0.20 * (1 - filtered["bio_penalty"]) +
        0.20 * (1 - filtered["recy_penalty"])
    )

    result = filtered.sort_values("final_score", ascending=False).head(top_k)

    return result[[
        "material_id",
        "material_type",
        "material_category",
        "predicted_cost_inr_per_kg",
        "predicted_co2_impact",
        "biodegradability_score",
        "recyclability_pct",
        "weight_capacity",
        "final_score"
    ]].to_dict(orient="records")

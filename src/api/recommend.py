import numpy as np
import pandas as pd

STRENGTH_MAPPING = {"Low": 1, "Medium": 2, "High": 3}

def _required_strength_from_fragility(fragility_level: str) -> str:
    # Simple rule: fragility drives minimum strength
    frag = (fragility_level or "Low").strip().title()
    if frag not in STRENGTH_MAPPING:
        frag = "Low"
    return frag

def rank_materials(materials_df: pd.DataFrame,
                   product: dict,
                   co2_model,
                   cost_model,
                   top_k: int = 5) -> list[dict]:

    # 1) basic constraints
    required_strength = _required_strength_from_fragility(product.get("fragility_level"))
    req_strength_val = STRENGTH_MAPPING[required_strength]

    # product weight in kg
    w_g = float(product.get("product_weight_g", 0) or 0)
    w_kg = w_g / 1000.0

    candidates = materials_df.copy()

    # must have strength_level >= required
    candidates["strength_encoded"] = candidates["strength_level"].map(STRENGTH_MAPPING).fillna(1).astype(int)
    candidates = candidates[candidates["strength_encoded"] >= req_strength_val]

    # must have weight_capacity >= product weight (basic)
    # (If your weight_capacity is not kg, adjust here. But don’t guess silently.)
    candidates = candidates[candidates["weight_capacity"] >= w_kg]

    if candidates.empty:
        return []

    # 2) model features
    X = candidates[[
        "strength_encoded",
        "weight_capacity",
        "biodegradability_score",
        "recyclability_pct",
        "cost_efficiency_index"
    ]].copy()

    # 3) predictions
    pred_co2 = co2_model.predict(X)
    pred_cost = cost_model.predict(X)

    candidates["predicted_co2_impact"] = pred_co2
    candidates["predicted_cost_inr_per_kg"] = pred_cost

    # 4) scoring (normalize within candidate set)
    def minmax(s):
        s = s.astype(float)
        return (s - s.min()) / (s.max() - s.min() + 1e-9)

    co2_n = minmax(candidates["predicted_co2_impact"])
    cost_n = minmax(candidates["predicted_cost_inr_per_kg"])

    # lower is better for both, so invert
    candidates["final_score"] = (
        0.45 * (1 - co2_n) +
        0.35 * (1 - cost_n) +
        0.20 * candidates["material_suitability_score"].astype(float)
    )

    out = (
        candidates.sort_values("final_score", ascending=False)
        .head(int(top_k))
        [[
            "material_id", "material_type", "material_category", "strength_level",
            "weight_capacity", "recyclability_pct", "biodegradability_score",
            "predicted_cost_inr_per_kg", "predicted_co2_impact", "final_score"
        ]]
        .to_dict(orient="records")
    )
    return out

import pandas as pd

def _safe_norm(series: pd.Series) -> pd.Series:
    max_val = series.max()
    if pd.isna(max_val) or max_val == 0:
        return pd.Series([0] * len(series), index=series.index)
    return series / max_val


def engineer_features(filtered_materials: pd.DataFrame, selected_product: pd.Series) -> pd.DataFrame:
    df = filtered_materials.copy()

    # ---- Normalized base features ----
    df["strength_score_norm"] = _safe_norm(df["strength_score"])
    df["recyclability_score"] = df["recyclability_percent"] / 100
    df["biodegradability_score_norm"] = df["biodegradability_score"] / 10

    # ---- CO2 and cost scores (lower is better) ----
    df["co2_score"] = 1 - _safe_norm(df["co2_emission_kg"])
    df["cost_score"] = 1 - _safe_norm(df["cost_per_unit_inr"])

    # ---- Product-material fit ----
    df["strength_margin"] = df["strength_score"] - selected_product["required_strength_score"]
    df["weight_fit_score"] = (df["weight_capacity_kg"] >= selected_product["product_weight_kg"]).astype(int)

    # ---- Fragility handling ----
    fragility_map = {"Low": 0.3, "Medium": 0.6, "High": 1.0}
    fragility_weight = fragility_map.get(str(selected_product["fragility_level"]), 0.6)

    # ---- Sustainability score ----
    df["sustainability_score"] = (
        0.40 * df["biodegradability_score_norm"] +
        0.30 * df["recyclability_score"] +
        0.30 * df["co2_score"]
    )

    # ---- Final suitability score ----
    df["material_suitability_score"] = (
        0.30 * df["strength_score_norm"] +
        0.25 * df["sustainability_score"] +
        0.20 * df["cost_score"] +
        0.15 * df["weight_fit_score"] +
        0.10 * (df["strength_score_norm"] * fragility_weight)
    )

    return df

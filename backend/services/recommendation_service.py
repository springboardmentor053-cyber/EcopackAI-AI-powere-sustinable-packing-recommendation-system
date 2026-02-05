import os
import joblib
import pandas as pd
import numpy as np


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

rf_model = joblib.load(os.path.join(MODEL_DIR, "rf_cost_model.pkl"))
xgb_model = joblib.load(os.path.join(MODEL_DIR, "xgb_co2_model.pkl"))


FEATURES = [
    "material_type",
    "strength",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_percentage",
    "fragility_level",
    "shipping_type"
]


def safe_normalize(series):
    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series([0] * len(series))

    return (series - min_val) / (max_val - min_val)


def run_recommendation(user_df):

    
    materials = [
        "glass", "plastic", "metal",
        "paper", "bagasse", "bamboo", "jute"
    ]

    expanded_rows = []
    for mat in materials:
        row = user_df.iloc[0].copy()
        row["material_type"] = mat
        expanded_rows.append(row)

    df = pd.DataFrame(expanded_rows)

    X = df[FEATURES]

    X = pd.get_dummies(
        X,
        columns=["material_type", "shipping_type"],
        drop_first=True
    )

    
    X = X.reindex(columns=rf_model.feature_names_in_, fill_value=0)

    df["predicted_cost"] = rf_model.predict(X)
    df["predicted_co2"] = xgb_model.predict(X)

    df["cost_norm"] = safe_normalize(df["predicted_cost"])
    df["co2_norm"] = safe_normalize(df["predicted_co2"])

    df["environmental_score"] = 1 - df["co2_norm"]

    df["rank_score"] = (
        0.5 * (1 - df["cost_norm"]) +
        0.5 * df["environmental_score"]
    )

    df = df.replace([np.inf, -np.inf], 0)
    df = df.fillna(0)

    result = df.sort_values("rank_score", ascending=False)

    return result[
        ["material_type", "predicted_cost",
         "predicted_co2", "environmental_score", "rank_score"]
    ].head(5)

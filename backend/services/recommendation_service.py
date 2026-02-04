import joblib
import pandas as pd

rf_model = joblib.load("models/rf_cost_model.pkl")
xgb_model = joblib.load("models/xgb_co2_model.pkl")

FEATURES = [
    "material_type",
    "strength",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_percentage",
    "fragility_level",
    "shipping_type"
]

def run_recommendation(df):

    X = df[FEATURES]

    X = pd.get_dummies(
        X,
        columns=["material_type", "shipping_type"],
        drop_first=True
    )

    X = X.reindex(columns=rf_model.feature_names_in_, fill_value=0)

    df["predicted_cost"] = rf_model.predict(X)
    df["predicted_co2"] = xgb_model.predict(X)

    
    df["cost_norm"] = (
        df["predicted_cost"] - df["predicted_cost"].min()
    ) / (
        df["predicted_cost"].max() - df["predicted_cost"].min()
    )

    df["co2_norm"] = (
        df["predicted_co2"] - df["predicted_co2"].min()
    ) / (
        df["predicted_co2"].max() - df["predicted_co2"].min()
    )

    df["rank_score"] = (
        0.5 * (1 - df["cost_norm"]) +
        0.5 * (1 - df["co2_norm"])
    )

    result = (
        df.groupby("material_type", as_index=False)
        .agg({
            "predicted_cost": "mean",
            "predicted_co2": "mean",
            "rank_score": "mean"
        })
        .sort_values("rank_score", ascending=False)
    )

    return result.head(5)

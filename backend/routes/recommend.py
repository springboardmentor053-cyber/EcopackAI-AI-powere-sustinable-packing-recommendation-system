from flask import Blueprint, request, jsonify
import joblib
import pandas as pd

from backend.db import load_materials, insert_recommendation_log
from src.feature_engineering import engineer_features

recommend_bp = Blueprint("recommend_bp", __name__)

# Load ML models once
cost_model = joblib.load("models/rf_cost_model.pkl")
co2_model = joblib.load("models/xgb_co2_model.pkl")
scaler = joblib.load("models/scaler.pkl")


@recommend_bp.route("/recommend", methods=["POST"])
def recommend_material():
    """
    Takes product input, recommends best material,
    logs analytics for BI dashboard.
    """

    data = request.get_json()

    # 1️⃣ Extract user inputs
    product_category = data.get("product_category")
    product_weight_kg = float(data.get("product_weight_kg"))
    fragility = data.get("fragility")

    # 2️⃣ Load materials dataset
    materials_df = load_materials()

    # 3️⃣ Feature engineering
    features_df = engineer_features(
        materials_df,
        product_category=product_category,
        product_weight_kg=product_weight_kg,
        fragility=fragility
    )

    # 4️⃣ Prepare ML inputs
    X = scaler.transform(features_df)

    # 5️⃣ Predictions
    features_df["predicted_cost"] = cost_model.predict(X)
    features_df["predicted_co2"] = co2_model.predict(X)

    # 6️⃣ Rank materials (simple logic)
    features_df["rank_score"] = (
        features_df["predicted_cost"] * 0.5 +
        features_df["predicted_co2"] * 0.5
    )

    features_df = features_df.sort_values("rank_score")

    # 7️⃣ Top recommendation
    top = features_df.iloc[0]

    recommended_material = top["material_name"]
    predicted_cost = float(top["predicted_cost"])
    predicted_co2 = float(top["predicted_co2"])

    # 8️⃣ Log for BI dashboard (Module 7 🔥)
    insert_recommendation_log(
        product_category=product_category,
        product_weight_kg=product_weight_kg,
        fragility=fragility,
        recommended_material=recommended_material,
        predicted_cost=predicted_cost,
        predicted_co2=predicted_co2
    )

    # 9️⃣ Response
    return jsonify({
        "recommended_material": recommended_material,
        "predicted_cost": round(predicted_cost, 2),
        "predicted_co2": round(predicted_co2, 2),
        "top_5_materials": features_df.head(5)[
            ["material_name", "predicted_cost", "predicted_co2"]
        ].to_dict(orient="records")
    })

from flask import Flask, request, jsonify
from flask_cors import CORS

from pathlib import Path
import os
import joblib
import pandas as pd

from backend.db import load_materials, load_products
from src.feature_engineering import engineer_features


# -----------------------------
# App setup
# -----------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent  # project root


# -----------------------------
# Basic API Security (simple)
# -----------------------------
# Frontend must send header: X-API-KEY: dev-key-123
API_KEY = os.getenv("ECO_API_KEY", "dev-key-123")


def require_api_key():
    """Returns (error_response, status_code) if unauthorized, else (None, None)."""
    client_key = request.headers.get("X-API-KEY")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return None, None


# -----------------------------
# Load ML models + scaler
# -----------------------------
MODELS_DIR = BASE_DIR / "models"

RF_COST_PATH = MODELS_DIR / "rf_cost_model.pkl"
XGB_CO2_PATH = MODELS_DIR / "xgb_co2_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

# Must match Module 4 feature order EXACTLY
ML_FEATURES = [
    "product_weight_kg",
    "required_strength_score",
    "preferred_biodegradability_score",
    "strength_score",
    "weight_capacity_kg",
    "biodegradability_score",
    "recyclability_percent",
    "co2_emission_kg",
    "cost_per_unit_inr",
]


def load_artifacts():
    """Load ML artifacts at startup."""
    for p in [RF_COST_PATH, XGB_CO2_PATH, SCALER_PATH]:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")

    rf_cost_model = joblib.load(RF_COST_PATH)
    xgb_co2_model = joblib.load(XGB_CO2_PATH)
    scaler = joblib.load(SCALER_PATH)

    return rf_cost_model, xgb_co2_model, scaler


rf_cost, xgb_co2, scaler = load_artifacts()


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return jsonify(
        {
            "message": "EcoPackAI backend running ✅",
            "try": ["/api/health", "/api/recommend (POST)"],
        }
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/recommend")
def recommend():
    # 1) Security check
    err, code = require_api_key()
    if err:
        return err, code

    # 2) Read JSON safely
    data = request.get_json(silent=True) or {}
    product_name = str(data.get("product_name", "")).strip()

    if not product_name:
        return jsonify({"error": "product_name is required"}), 400

    # 3) Load from PostgreSQL (live)
    try:
        materials_df = load_materials()
        products_df = load_products()
    except Exception as e:
        return jsonify({"error": f"Database load failed: {str(e)}"}), 500

    # 4) Match product (case-insensitive)
    match = products_df[products_df["product_name"].str.lower() == product_name.lower()]
    if match.empty:
        return jsonify({"error": f"Product '{product_name}' not found"}), 400

    selected_product = match.iloc[0]

    # 5) Rule-based material filtering (Module 2 baseline)
    filtered_materials = materials_df[
        (materials_df["strength_score"] >= selected_product["required_strength_score"])
        & (
            materials_df["biodegradability_score"]
            >= selected_product["preferred_biodegradability_score"]
        )
        & (materials_df["cost_per_unit_inr"] <= selected_product["max_packaging_cost_inr"])
    ].copy()

    if filtered_materials.empty:
        return jsonify({"error": "No materials matched your requirements"}), 200

    # 6) Feature engineering + suitability ranking
    fe_df = engineer_features(filtered_materials, selected_product)
    ranked = (
        fe_df.sort_values("material_suitability_score", ascending=False).head(10).copy()
    )

    # 7) Add product-level fields required for ML input
    ranked["product_weight_kg"] = float(selected_product["product_weight_kg"])
    ranked["required_strength_score"] = float(selected_product["required_strength_score"])
    ranked["preferred_biodegradability_score"] = float(
        selected_product["preferred_biodegradability_score"]
    )

    # 8) ML predictions
    X_pred = ranked[ML_FEATURES].copy()
    X_pred_scaled = scaler.transform(X_pred)

    ranked["pred_cost_inr"] = rf_cost.predict(X_pred_scaled)
    ranked["pred_co2_kg"] = xgb_co2.predict(X_pred_scaled)

    # 9) Environmental score (0–100, higher is better)
    #    We reward high biodegradability + recyclability and penalize higher CO2.
    max_co2 = float(ranked["pred_co2_kg"].max()) if len(ranked) > 0 else 1.0
    if max_co2 == 0:
        max_co2 = 1.0

    ranked["co2_score_norm"] = 1 - (ranked["pred_co2_kg"] / max_co2)
    ranked["environment_score"] = (
        0.40 * (ranked["biodegradability_score"] / 10)
        + 0.40 * (ranked["recyclability_percent"] / 100)
        + 0.20 * ranked["co2_score_norm"]
    ) * 100

    # 10) Build JSON response
    results = []
    for i, row in ranked.reset_index(drop=True).iterrows():
        results.append(
            {
                "rank": int(i + 1),
                "material_name": row["material_name"],
                "pred_cost_inr": float(row["pred_cost_inr"]),
                "pred_co2_kg": float(row["pred_co2_kg"]),
                "recyclability_percent": float(row["recyclability_percent"]),
                "biodegradability_score": float(row["biodegradability_score"]),
                "suitability_score": float(row["material_suitability_score"]),
                "environment_score": float(row["environment_score"]),
            }
        )

    return jsonify(
        {
            "product": {
                "product_name": selected_product["product_name"],
                "product_category": selected_product["product_category"],
                "product_weight_kg": float(selected_product["product_weight_kg"]),
                "fragility_level": selected_product.get("fragility_level", ""),
                "temperature_sensitive": selected_product.get("temperature_sensitive", ""),
            },
            "recommendations": results,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)

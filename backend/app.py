from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from pathlib import Path
import os
import joblib
import pandas as pd

from backend.db import load_materials, load_products
from src.feature_engineering import engineer_features

# -----------------------------
# Project paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"

# -----------------------------
# App setup
# -----------------------------
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path="/static",
)

CORS(app)

# -----------------------------
# Basic API Security
# -----------------------------
API_KEY = os.getenv("ECO_API_KEY", "dev-key-123")


def require_api_key():
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

# IMPORTANT: column names + order must match training
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
    for p in [RF_COST_PATH, XGB_CO2_PATH, SCALER_PATH]:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")

    rf_cost_model = joblib.load(RF_COST_PATH)
    xgb_co2_model = joblib.load(XGB_CO2_PATH)
    scaler_obj = joblib.load(SCALER_PATH)
    return rf_cost_model, xgb_co2_model, scaler_obj


rf_cost, xgb_co2, scaler = load_artifacts()

# -----------------------------
# Helpers
# -----------------------------
def _to_num(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Convert columns to numeric safely."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _safe_float(x, default=0.0) -> float:
    try:
        v = float(x)
        if pd.isna(v):
            return float(default)
        return v
    except Exception:
        return float(default)


def _safe_int(x, default=10) -> int:
    try:
        v = int(float(x))
        return v
    except Exception:
        return int(default)


# -----------------------------
# UI Routes
# -----------------------------
@app.get("/")
def landing():
    return render_template("landing.html")


@app.get("/wizard")
def wizard_page():
    return render_template("wizard.html")


@app.get("/results")
def results_page():
    return render_template("results.html")


@app.get("/comparison")
def comparison_page():
    return render_template("comparison.html")


# ✅ Alias routes (so .html also works)
@app.get("/landing.html")
def landing_html():
    return render_template("landing.html")


@app.get("/wizard.html")
def wizard_html():
    return render_template("wizard.html")


@app.get("/results.html")
def results_html():
    return render_template("results.html")


@app.get("/comparison.html")
def comparison_html():
    return render_template("comparison.html")


@app.get("/api")
def api_root():
    return jsonify({"message": "EcoPackAI backend running ✅", "try": ["/api/health", "/api/recommend (POST)"]})


# -----------------------------
# API Routes
# -----------------------------
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/recommend")
def recommend():
    err, code = require_api_key()
    if err:
        return err, code

    data = request.get_json(silent=True) or {}
    product_name = str(data.get("product_name", "")).strip()
    if not product_name:
        return jsonify({"error": "product_name is required"}), 400

    # ✅ NEW: top_n from request (clamped to 1..20)
    top_n = _safe_int(data.get("top_n", 10), 10)
    top_n = max(1, min(top_n, 20))

    # Load DB data
    try:
        materials_df = load_materials()
        products_df = load_products()
    except Exception as e:
        return jsonify({"error": f"Database load failed: {str(e)}"}), 500

    # Normalize key columns
    products_df["product_name"] = products_df["product_name"].astype(str)
    materials_df["material_name"] = materials_df["material_name"].astype(str)

    # Ensure numeric fields
    materials_df = _to_num(
        materials_df,
        [
            "strength_score",
            "biodegradability_score",
            "cost_per_unit_inr",
            "weight_capacity_kg",
            "recyclability_percent",
            "co2_emission_kg",
        ],
    )
    products_df = _to_num(
        products_df,
        [
            "product_weight_kg",
            "required_strength_score",
            "preferred_biodegradability_score",
            "max_packaging_cost_inr",
        ],
    )

    match = products_df[products_df["product_name"].str.lower() == product_name.lower()]
    if match.empty:
        return jsonify({"error": f"Product '{product_name}' not found"}), 400

    selected_product = match.iloc[0]

    req_strength = _safe_float(selected_product.get("required_strength_score"), 0)
    pref_bio = _safe_float(selected_product.get("preferred_biodegradability_score"), 0)
    max_cost = _safe_float(selected_product.get("max_packaging_cost_inr"), 0)

    # Filter materials
    filtered_materials = materials_df.dropna(
        subset=["strength_score", "biodegradability_score", "cost_per_unit_inr"]
    ).copy()

    filtered_materials = filtered_materials[
        (filtered_materials["strength_score"] >= req_strength)
        & (filtered_materials["biodegradability_score"] >= pref_bio)
        & (filtered_materials["cost_per_unit_inr"] <= max_cost)
    ].copy()

    if filtered_materials.empty:
        return jsonify({"error": "No materials matched your requirements"}), 200

    # Feature engineering + rank
    fe_df = engineer_features(filtered_materials, selected_product)
    if "material_suitability_score" not in fe_df.columns:
        return jsonify({"error": "Feature engineering failed: 'material_suitability_score' missing"}), 500

    # ✅ use top_n instead of fixed 10
    ranked = fe_df.sort_values("material_suitability_score", ascending=False).head(top_n).copy()

    # Add product fields required by ML feature list
    ranked["product_weight_kg"] = _safe_float(selected_product.get("product_weight_kg"), 0)
    ranked["required_strength_score"] = req_strength
    ranked["preferred_biodegradability_score"] = pref_bio

    # Ensure all ML features exist
    for c in ML_FEATURES:
        if c not in ranked.columns:
            ranked[c] = 0.0

    ranked = _to_num(ranked, ML_FEATURES).fillna(0)

    # IMPORTANT: keep exact column order
    X_pred = ranked[ML_FEATURES].copy()

    # ✅ MATCH NOTEBOOK:
    # - RF COST model: trained on UN-SCALED X
    # - XGB CO2 model: trained on SCALED X
    ranked["pred_cost_inr"] = rf_cost.predict(X_pred)
    ranked["pred_co2_kg"] = xgb_co2.predict(scaler.transform(X_pred))

    # Environment score
    max_co2 = float(pd.to_numeric(ranked["pred_co2_kg"], errors="coerce").max() or 1.0)
    if max_co2 <= 0:
        max_co2 = 1.0

    ranked["co2_score_norm"] = 1 - (ranked["pred_co2_kg"] / max_co2)
    ranked["environment_score"] = (
        0.40 * (ranked["biodegradability_score"] / 10)
        + 0.40 * (ranked["recyclability_percent"] / 100)
        + 0.20 * ranked["co2_score_norm"]
    ) * 100

    # Response
    results = []
    for i, row in ranked.reset_index(drop=True).iterrows():
        results.append(
            {
                "rank": int(i + 1),
                "material_name": str(row.get("material_name", "")),
                "pred_cost_inr": float(row.get("pred_cost_inr", 0.0)),
                "pred_co2_kg": float(row.get("pred_co2_kg", 0.0)),
                "recyclability_percent": float(row.get("recyclability_percent", 0.0)),
                "biodegradability_score": float(row.get("biodegradability_score", 0.0)),
                "suitability_score": float(row.get("material_suitability_score", 0.0)),
                "environment_score": float(row.get("environment_score", 0.0)),
            }
        )

    return jsonify(
        {
            "product": {
                "product_name": str(selected_product.get("product_name", "")),
                "product_category": str(selected_product.get("product_category", "")),
                "product_weight_kg": _safe_float(selected_product.get("product_weight_kg"), 0),
                "fragility_level": str(selected_product.get("fragility_level", "")),
                "temperature_sensitive": str(selected_product.get("temperature_sensitive", "")),
            },
            "top_n": top_n,
            "recommendations": results,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)

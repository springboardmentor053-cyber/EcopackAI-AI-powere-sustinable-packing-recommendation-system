from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import pandas as pd

from src.pipelines.model_loader import load_models
from src.api.recommend import rank_materials

# -------------------------------------------------
# App setup
# -------------------------------------------------
load_dotenv()
app = Flask(__name__)

# -------------------------------------------------
# Load ML models once
# -------------------------------------------------
co2_model, cost_model = load_models()

# Load materials dataset (CSV for now)
materials_df = pd.read_csv(
    "E:/Data Science/EcoPackAI/data/processed/materials_featured.csv"
)

# -------------------------------------------------
# Strength mapping (human → numeric)
# -------------------------------------------------
STRENGTH_MAP = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/recommend")
def recommend():
    try:
        payload = request.get_json(silent=True) or {}

        # ---- Required mentor-style inputs ----
        required_fields = [
            "strength_level",
            "product_weight_g",
            "biodegradability_score",
            "recyclability_pct"
        ]

        missing = [f for f in required_fields if f not in payload]
        if missing:
            return jsonify({
                "error": "missing_fields",
                "fields": missing
            }), 400

        # ---- Normalize & validate inputs ----
        strength_level = payload["strength_level"].strip().title()
        if strength_level not in STRENGTH_MAP:
            return jsonify({
                "error": "invalid_strength_level",
                "allowed": ["Low", "Medium", "High"]
            }), 400

        product_constraints = {
            "strength_encoded": STRENGTH_MAP[strength_level],
            "product_weight_g": float(payload["product_weight_g"]),
            "biodegradability_score": float(payload["biodegradability_score"]),
            "recyclability_pct": float(payload["recyclability_pct"])
        }

        # ---- Run recommendation engine ----
        results = rank_materials(
            materials_df=materials_df,
            product=product_constraints,
            co2_model=co2_model,
            cost_model=cost_model,
            top_k=3
        )

        return jsonify({
            "inputs": {
                "strength_level": strength_level,
                "product_weight_g": product_constraints["product_weight_g"],
                "biodegradability_score": product_constraints["biodegradability_score"],
                "recyclability_pct": product_constraints["recyclability_pct"]
            },
            "recommendations": results,
            "count": len(results)
        })

    except Exception as e:
        return jsonify({
            "error": "internal_error",
            "message": str(e)
        }), 500

# -------------------------------------------------
# Run app
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
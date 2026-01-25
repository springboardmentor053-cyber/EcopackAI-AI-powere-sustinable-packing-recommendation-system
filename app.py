from flask import Flask, request, jsonify
from dotenv import load_dotenv
import pandas as pd

from src.utils.config import settings
from src.pipelines.model_loader import load_models
from src.api.recommend import rank_materials

load_dotenv()

app = Flask(__name__)

# Load once at startup (fast API)
co2_model, cost_model = load_models()

# Load featured materials once (later you’ll fetch from DB; do CSV first to stabilize)
materials_df = pd.read_csv("E:/Data Science/EcoPackAI/data/processed/materials_featured.csv")

def require_api_key():
    if not settings.API_KEY:
        return True
    return request.headers.get("X-API-KEY", "") == settings.API_KEY

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/recommend")
def recommend():
    if not require_api_key():
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}

    # REQUIRED fields for your current rule set
    missing = []
    if "product_weight_g" not in payload: missing.append("product_weight_g")
    if "fragility_level" not in payload: missing.append("fragility_level")

    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400

    top_k = int(payload.get("top_k", settings.TOP_K_DEFAULT))

    results = rank_materials(
        materials_df=materials_df,
        product=payload,
        co2_model=co2_model,
        cost_model=cost_model,
        top_k=top_k
    )

    return jsonify({
        "product": {
            "product_weight_g": payload.get("product_weight_g"),
            "fragility_level": payload.get("fragility_level")
        },
        "recommendations": results,
        "count": len(results)
    })

if __name__ == "__main__":
    app.run(debug=True)
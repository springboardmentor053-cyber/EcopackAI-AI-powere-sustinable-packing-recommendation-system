from flask import Flask, request, jsonify, render_template
import pandas as pd
from dotenv import load_dotenv

from src.api.recommend import rank_materials
from src.pipelines.model_loader import load_models

load_dotenv()

app = Flask(__name__)

co2_model, cost_model = load_models()

materials_df = pd.read_sql(fetch_materials(), engine)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/recommend")
def recommend():
    try:
        payload = request.get_json(force=True)

        required_fields = [
            "strength_level",
            "product_weight_g",
            "biodegradability_score",
            "recyclability_pct"
        ]

        missing = [f for f in required_fields if f not in payload]
        if missing:
            return jsonify({"error": "missing_fields", "fields": missing}), 400

        results = rank_materials(
            materials_df=materials_df,
            product=payload,
            co2_model=co2_model,
            cost_model=cost_model,
            top_k=3
        )

        return jsonify({
            "product": payload,
            "recommendations": results,
            "count": len(results)
        })

    except Exception as e:
        return jsonify({
            "error": "internal_error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
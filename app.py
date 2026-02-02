from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os

# ✅ CREATE APP FIRST
app = Flask(__name__)
CORS(app)

# Base directory
BASE_DIR = os.path.dirname(__file__)

# Load trained models
cost_model = joblib.load(os.path.join(BASE_DIR, "models", "cost_model.pkl"))
co2_model = joblib.load(os.path.join(BASE_DIR, "models", "co2_model.pkl"))

# ✅ ROUTES COME AFTER app IS DEFINED
@app.route("/", methods=["GET"])
def home():
    return "EcoPackAI backend is running"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required_fields = [
        "strength_mpa",
        "biodegradability_score",
        "recyclability_percent",
        "flexibility",
        "cost_per_unit",
        "co2_emission_score"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Encode flexibility
    flexibility_map = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    flexibility_value = data["flexibility"]

    if isinstance(flexibility_value, str):
        flexibility_encoded = flexibility_map.get(flexibility_value)
    else:
        flexibility_encoded = int(flexibility_value)

    if flexibility_encoded is None:
        return jsonify({
            "error": "flexibility must be Low, Medium, or High"
        }), 400

    # Features for models
    cost_features = np.array([[
        float(data["strength_mpa"]),
        float(data["biodegradability_score"]),
        float(data["recyclability_percent"]),
        float(data["co2_emission_score"]),
        float(flexibility_encoded)
    ]])

    co2_features = np.array([[
        float(data["strength_mpa"]),
        float(data["biodegradability_score"]),
        float(data["recyclability_percent"]),
        float(data["cost_per_unit"]),
        float(flexibility_encoded)
    ]])

    cost = float(cost_model.predict(cost_features)[0])
    co2 = float(co2_model.predict(co2_features)[0])

    suggestion = (
        "Switch to recycled materials"
        if co2 > 50 else
        "Sustainable material choice"
    )

    return jsonify({
        "predicted_cost": round(cost, 2),
        "predicted_co2": round(co2, 2),
        "suggestion": suggestion
    })

# ✅ START SERVER LAST
if __name__ == "__main__":
    app.run(debug=True)

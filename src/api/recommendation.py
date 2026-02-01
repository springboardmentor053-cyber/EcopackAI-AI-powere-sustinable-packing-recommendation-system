from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os

app = Flask(__name__)

# -------------------------------------------------
# Load models
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COST_MODEL_PATH = os.path.join(BASE_DIR, "models", "cost_model.pkl")
CO2_MODEL_PATH = os.path.join(BASE_DIR, "models", "co2_model.pkl")

cost_model = joblib.load(COST_MODEL_PATH)
co2_model = joblib.load(CO2_MODEL_PATH)

# -------------------------------------------------
# Input validation
# -------------------------------------------------
def validate_input(data):
    required_fields = [
        "strength_encoded",
        "weight_capacity",
        "biodegradability_score",
        "recyclability_pct",
        "cost_efficiency_index"
    ]

    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    return True, None

# -------------------------------------------------
# Recommendation / Prediction API
# -------------------------------------------------
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json or {}

    is_valid, error_msg = validate_input(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    try:
        input_df = pd.DataFrame([data])

        predicted_cost = cost_model.predict(input_df)[0]
        predicted_co2 = co2_model.predict(input_df)[0]

        return jsonify({
            "predicted_cost": float(predicted_cost),
            "predicted_co2": float(predicted_co2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

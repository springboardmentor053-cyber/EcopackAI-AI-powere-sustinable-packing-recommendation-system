from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load trained models
cost_model = joblib.load("E:/Data Science/EcoPackAI/models/cost_model.pkl")
co2_model = joblib.load("E:/Data Science/EcoPackAI/models/co2_model.pkl")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    # Convert input JSON to DataFrame
    input_df = pd.DataFrame([data])

    # Predictions
    predicted_cost = cost_model.predict(input_df)[0]
    predicted_co2 = co2_model.predict(input_df)[0]

    return jsonify({
        "predicted_cost": float(predicted_cost),
        "predicted_co2": float(predicted_co2)
    })

if __name__ == "__main__":
    app.run(debug=True)
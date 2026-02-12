from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load trained models
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

cost_model = joblib.load(os.path.join(MODEL_DIR, "cost_model.pkl"))
co2_model = joblib.load(os.path.join(MODEL_DIR, "co2_model.pkl"))

# Load materials data for recommendation
MATERIALS_PATH = os.path.join(BASE_DIR, "..", "..", "..", "data", "materials_final.csv")
materials_df = pd.read_csv(MATERIALS_PATH)

# Clean column names (safety)
materials_df.columns = materials_df.columns.str.strip().str.lower()
print(materials_df.head())

print(materials_df.columns.tolist())


#@app.route("/")
#def home():
#    return "Backend is running"
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK",
        "message": "EcoPackAI Flask backend is running"
    })
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Prepare input for ML models
    input_features = np.array([[
        data["weight_capacity_score"],
        data["strength_score"],
        data["barrier_score"],
        data["reuse_potential_score"],
        data["material_strength"],
        data["biodegradability"],
        data["recyclability_percent"]
    ]])

    predicted_cost = cost_model.predict(input_features)[0]
    predicted_co2 = co2_model.predict(input_features)[0]

    # Copy materials dataframe 
    df = materials_df.copy()

    # Calculate material score (CORRECT COLUMNS) 
    df["material_score"] = (
        predicted_cost +
        predicted_co2 -
        df["strength_score"] -
        df["recyclability_percent"] -
        df["biodegradability_score"]
    )


    #  Sort & select Top 5
    top_materials = df.sort_values("material_score").head(5)

    # Prepare response
    results = top_materials[[
        "material_name",
        "strength_score",
        "recyclability_percent",
        "biodegradability_score",
        "co2_emission_score",
        "material_score"
    ]].to_dict(orient="records")

    return jsonify({
        "predicted_cost": round(float(predicted_cost), 2),
        "predicted_co2": round(float(predicted_co2), 2),
        "recommended_materials": results
    })
@app.route("/")
def home():
    return "EcoPackAI Backend is running"



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

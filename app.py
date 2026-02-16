from flask import Flask, request, jsonify, send_file
import joblib
import numpy as np
import pandas as pd
from flask_cors import CORS
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    print("✅ Connected to PostgreSQL")
else:
    print("❌ DATABASE_URL not found")


# Initialize Flask app
app = Flask(__name__)
last_top_materials = None
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
    print("Incoming Data:", data)

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

    global last_top_materials
    last_top_materials = top_materials


        # ----- CO2 Reduction Calculation -----
    avg_recommended_co2 = top_materials["co2_emission_score"].mean()

    if predicted_co2 != 0:
        co2_reduction_percent = ((predicted_co2 - avg_recommended_co2) / predicted_co2) * 100
    else:
        co2_reduction_percent = 0

    co2_reduction_percent = round(co2_reduction_percent, 2)


    # ----- Correct Cost Savings Calculation -----

    # Simulated baseline cost (example logic)
    baseline_cost = 10   # assume traditional packaging cost baseline

    if baseline_cost != 0:
        cost_savings_percent = ((baseline_cost - predicted_cost) / baseline_cost) * 100
    else:
        cost_savings_percent = 0

    cost_savings_percent = round(cost_savings_percent, 2)


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
        "co2_reduction_percent": round(float(co2_reduction_percent), 2),
        "cost_savings_percent": round(float(cost_savings_percent), 2),
        "recommended_materials": results
    })

from flask import send_file

@app.route("/export_excel")
def export_excel():
    global last_top_materials
    if last_top_materials is None:
        return jsonify({"error": "Run /predict first"}), 400
    import os
    file_path = os.path.join(os.getcwd(), "report.xlsx")
    # Save file properly
    last_top_materials.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

@app.route("/")
def home():
    return "EcoPackAI Backend is running"



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


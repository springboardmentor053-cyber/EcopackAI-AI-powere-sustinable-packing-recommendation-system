from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os
import psycopg2

app = Flask(__name__)

# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COST_MODEL_PATH = os.path.join(BASE_DIR, "models", "cost_model.pkl")
CO2_MODEL_PATH = os.path.join(BASE_DIR, "models", "co2_model.pkl")

cost_model = joblib.load(COST_MODEL_PATH)
co2_model = joblib.load(CO2_MODEL_PATH)

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
def get_db_connection():
    return psycopg2.connect(
        dbname="EcoPackAI_Database",
        user="postgres",
        password="Gaurav@123",
        host="localhost",
        port="5432"
    )

# -------------------------------------------------
# HELPER
# -------------------------------------------------
def encode_strength(mpa):
    if mpa < 20:
        return 0
    elif mpa < 50:
        return 1
    else:
        return 2

# -------------------------------------------------
# MAIN RECOMMEND API
# -------------------------------------------------
@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.json or {}

    try:
        # -----------------------
        # USER INPUT
        # -----------------------
        strength_mpa = float(data["strength_mpa"])
        weight_capacity = float(data["weight_capacity"])
        biodegradability_score = float(data["biodegradability_score"])
        recyclability_pct = float(data["recyclability_pct"])
        cost_inr_per_kg = float(data["cost_inr_per_kg"])

        if cost_inr_per_kg == 0:
            return jsonify({"error": "Cost cannot be zero"}), 400

        # -----------------------
        # FEATURE ENGINEERING
        # -----------------------
        strength_encoded = encode_strength(strength_mpa)
        cost_efficiency_index = strength_mpa / cost_inr_per_kg

        user_input_df = pd.DataFrame([{
            "strength_encoded": strength_encoded,
            "weight_capacity": weight_capacity,
            "biodegradability_score": biodegradability_score,
            "recyclability_pct": recyclability_pct,
            "cost_efficiency_index": cost_efficiency_index
        }])

        # -----------------------
        # SINGLE PREDICTION
        # -----------------------
        predicted_cost = cost_model.predict(user_input_df)[0]
        predicted_co2 = co2_model.predict(user_input_df)[0]

        # -----------------------
        # LOAD MATERIALS FROM DB
        # -----------------------
        conn = get_db_connection()
        materials_df = pd.read_sql("SELECT * FROM materials", conn)
        conn.close()

        # -----------------------
        # FEATURE ENGINEERING FOR DB MATERIALS
        # -----------------------
        materials_df["strength_encoded"] = materials_df["strength_mpa"].apply(encode_strength)
        materials_df["cost_efficiency_index"] = (
            materials_df["strength_mpa"] /
            materials_df["cost_inr_per_kg"]
        )

        X = materials_df[[
            "strength_encoded",
            "weight_capacity",
            "biodegradability_score",
            "recyclability_pct",
            "cost_efficiency_index"
        ]]

        materials_df["predicted_cost"] = cost_model.predict(X)
        materials_df["predicted_co2"] = co2_model.predict(X)

        # -----------------------
        # RANKING
        # -----------------------
        materials_df["rank_cost"] = materials_df["predicted_cost"].rank()
        materials_df["rank_co2"] = materials_df["predicted_co2"].rank()

        materials_df["final_score"] = (
            0.5 * materials_df["rank_cost"] +
            0.5 * materials_df["rank_co2"]
        )

        ranked = materials_df.sort_values("final_score").head(5)

        recommendations = ranked[[
            "material_type",
            "predicted_cost",
            "predicted_co2"
        ]]

        return jsonify({
            "predicted_cost": round(float(predicted_cost), 2),
            "predicted_co2": round(float(predicted_co2), 2),
            "recommendations": recommendations.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

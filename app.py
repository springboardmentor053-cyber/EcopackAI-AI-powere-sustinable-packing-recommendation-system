from flask import Flask, request, jsonify, send_from_directory
import joblib
import pandas as pd
import numpy as np
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

cost_model = joblib.load("models/cost_model.pkl")
co2_model = joblib.load("models/co2_model.pkl")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

def get_db_connection():
    return psycopg2.connect(
        dbname="EcoPackAI_Database",
        user="postgres",
        password="Gaurav@123",
        host="localhost",
        port="5432"
    )

def strength_to_encoded(mpa):
    if mpa < 20:
        return 0
    elif mpa < 50:
        return 1
    else:
        return 2

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/style.css")
def css():
    return send_from_directory(FRONTEND_DIR, "style.css")

@app.route("/app.js")
def js():
    return send_from_directory(FRONTEND_DIR, "app.js")

@app.route("/materials")
def materials_page():
    return send_from_directory(FRONTEND_DIR, "materials.html")

@app.route("/api/materials")
def api_materials():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM materials ORDER BY material_id;")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({"materials": rows})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    df = pd.DataFrame([data])

    if "strength_mpa" in df.columns and "cost_inr_per_kg" in df.columns:
        df["cost_efficiency_index"] = df["strength_mpa"] / df["cost_inr_per_kg"]
        df["strength_encoded"] = df["strength_mpa"].apply(strength_to_encoded)

    required_cols = list(cost_model.feature_names_in_)
    X = df.reindex(columns=required_cols, fill_value=0)
    X = X.replace([np.inf, -np.inf], 0)

    predicted_cost = cost_model.predict(X)[0]
    predicted_co2 = co2_model.predict(X)[0]

    return jsonify({
        "predicted_cost": float(predicted_cost),
        "predicted_co2": float(predicted_co2)
    })

if __name__ == "__main__":
    app.run(debug=True)

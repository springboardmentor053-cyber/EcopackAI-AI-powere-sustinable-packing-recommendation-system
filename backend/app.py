from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import joblib
import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv
# ---------------- APP INIT ----------------
load_dotenv()

app = Flask(
    __name__,
    static_folder="../Frontend",
    static_url_path="/static"
)
# ---------------- DATABASE ----------------
def get_db_connection():

    # Render Environment Variable
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # --- RENDER CLOUD DATABASE ---
    if DATABASE_URL:
        result = urlparse(DATABASE_URL)
        
    return psycopg2.connect(
        dbname="ecopackai_6qi1",
        user="ecopack_user",
        password="R0MNhnqwOD19NfzBDw0E0fKFleKkZlLY",
        host="dpg-d6eoik15pdvs73fvqrgg-a.singapore-postgres.render.com",
        port="5432",
        sslmode="require"
    )
    
     # --- LOCAL DATABASE --- #
    return psycopg2.connect(
        dbname="EcoPackAI_Database",
        user="postgres",
        password="Gaurav@123",
        host="127.0.0.1",
        port="5432"
    )
# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")
MODELS_DIR = os.path.join(BASE_DIR, "models")

cost_model = joblib.load(os.path.join(MODELS_DIR, "cost_model.pkl"))
co2_model = joblib.load(os.path.join(MODELS_DIR, "co2_model.pkl"))

# ---------------- HELPER ----------------
def encode_strength(mpa):
    if mpa < 20:
        return 0
    elif mpa < 50:
        return 1
    else:
        return 2


# =====================================================
# ===================== API ROUTES ====================
# =====================================================

#  MATERIALS API
@app.route("/api/materials")
def get_materials():
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM materials", conn)
        conn.close()

        return jsonify({
            "materials": df.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        strength_mpa = float(data["strength_mpa"])
        weight_capacity = float(data["weight_capacity"])
        biodegradability_score = float(data["biodegradability_score"])
        recyclability_pct = float(data["recyclability_pct"])
        cost_inr_per_kg = float(data["cost_inr_per_kg"])

        strength_encoded = encode_strength(strength_mpa)
        cost_efficiency_index = strength_mpa / cost_inr_per_kg

        input_df = pd.DataFrame([{
            "strength_encoded": strength_encoded,
            "weight_capacity": weight_capacity,
            "biodegradability_score": biodegradability_score,
            "recyclability_pct": recyclability_pct,
            "cost_efficiency_index": cost_efficiency_index
        }])

        predicted_cost = cost_model.predict(input_df)[0]
        predicted_co2 = co2_model.predict(input_df)[0]

        return jsonify({
            "predicted_cost": float(predicted_cost),
            "predicted_co2": float(predicted_co2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM materials", conn)
        conn.close()

        df["strength_encoded"] = df["strength_mpa"].apply(encode_strength)
        df["cost_efficiency_index"] = df["strength_mpa"] / df["cost_inr_per_kg"]

        X = df[[
            "strength_encoded",
            "weight_capacity",
            "biodegradability_score",
            "recyclability_pct",
            "cost_efficiency_index"
        ]]

        df["predicted_cost"] = cost_model.predict(X)
        df["predicted_co2"] = co2_model.predict(X)

        df["rank_score"] = (
            df["predicted_cost"].rank() +
            df["predicted_co2"].rank()
        )

        top5 = df.sort_values("rank_score").head(5)

        return jsonify({
            "recommendations": top5[[
                "material_type",
                "predicted_cost",
                "predicted_co2"
            ]].to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/dashboard-data")
def dashboard_data():
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM materials", conn)
        conn.close()

        df["strength_encoded"] = df["strength_mpa"].apply(encode_strength)
        df["cost_efficiency_index"] = df["strength_mpa"] / df["cost_inr_per_kg"]

        X = df[[
            "strength_encoded",
            "weight_capacity",
            "biodegradability_score",
            "recyclability_pct",
            "cost_efficiency_index"
        ]]

        df["predicted_cost"] = cost_model.predict(X)
        df["predicted_co2"] = co2_model.predict(X)

        return jsonify({
            "total_materials": int(len(df)),
            "avg_cost": float(df["predicted_cost"].mean()),
            "avg_co2": float(df["predicted_co2"].mean()),
            "materials": df[[
                "material_type",
                "predicted_cost",
                "predicted_co2"
            ]].to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================
# ================= PAGE ROUTES =======================
# =====================================================

@app.route("/")
def recommendation_page():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/materials")
def materials_page():
    return send_from_directory(FRONTEND_DIR, "materials.html")

@app.route("/dashboard")
def dashboard_page():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


# =====================================================
# ================= RUN APP ===========================
# =====================================================

if __name__ == "__main__":
    app.run()

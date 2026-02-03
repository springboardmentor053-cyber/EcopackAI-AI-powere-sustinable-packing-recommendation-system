import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
import psycopg2


# LOAD ENV


load_dotenv()

CO2_MODEL_PATH = os.getenv("CO2_MODEL_PATH")
COST_MODEL_PATH = os.getenv("COST_MODEL_PATH")
LOG_FILE = os.getenv("LOG_FILE", "ecopackai.log")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

os.makedirs("logs", exist_ok=True)


# LOGGING


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EcoPackAI")


# APP


app = Flask(__name__)
CORS(app)


# LOAD MATERIALS FROM POSTGRESQL


def load_materials_from_db():

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    df = pd.read_sql("SELECT * FROM materials", conn)
    conn.close()

    df["material_name"] = df["material_name"].str.strip()

    return df


materials = load_materials_from_db()
logger.info("Materials loaded from PostgreSQL")


# FEATURE COLUMNS


feature_cols = [
    "strength",
    "weight_capacity",
    "durability_score",
    "biodegradability_score",
    "recyclability_percent"
]


# SCALER


scaler = StandardScaler()
scaler.fit(materials[feature_cols])


# LOAD MODELS


def load_model(path, name):
    try:
        model = joblib.load(path)
        logger.info(f"{name} model loaded")
        return model, True
    except Exception as e:
        logger.error(f"{name} model load failed: {e}")
        return None, False


co2_model, use_co2_model = load_model(CO2_MODEL_PATH, "CO2")
cost_model, use_cost_model = load_model(COST_MODEL_PATH, "Cost")


# HEALTH CHECK


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "EcoPackAI backend running",
        "db_connected": True,
        "co2_model_loaded": use_co2_model,
        "cost_model_loaded": use_cost_model
    })


# VALIDATION


def validate_inputs(data, required):

    if not data:
        return "No input JSON provided"

    for field in required:
        if field not in data:
            return f"Missing field: {field}"

    try:
        if int(data["quantity"]) <= 0:
            return "Quantity must be > 0"

        if float(data["baseline_co2"]) <= 0:
            return "Baseline CO2 must be > 0"

    except:
        return "Numeric fields invalid"

    return None


# MAIN API


@app.route("/recommend", methods=["POST"])
def recommend_material():

    try:

        data = request.json

        required_fields = [
            "strength_encoded",
            "weight_capacity",
            "biodegradability_score",
            "recyclability_percent",
            "cost_efficiency_score",
            "quantity",
            "baseline_co2"
        ]

        error = validate_inputs(data, required_fields)
        if error:
            return jsonify({"error": error}), 400

        product_name = data.get("product_name", "Generic Product")
        quantity = int(data["quantity"])
        baseline_co2 = float(data["baseline_co2"])

        strength = float(data["strength_encoded"])
        weight_capacity = float(data["weight_capacity"])
        biodegradability = float(data["biodegradability_score"])
        recyclability = float(data["recyclability_percent"])
        cost_efficiency = float(data["cost_efficiency_score"])

        logger.info(
            f"Inputs: strength={strength}, weight={weight_capacity}, "
            f"bio={biodegradability}, recycle={recyclability}, "
            f"cost_eff={cost_efficiency}"
        )

        # ---------------- CO2 ----------------

        if use_co2_model:
            co2_input = pd.DataFrame([{
                "strength": strength,
                "weight_capacity": weight_capacity,
                "durability_score": 5,
                "biodegradability_score": biodegradability,
                "recyclability_percent": recyclability
            }])

            predicted_co2 = float(
                co2_model.predict(scaler.transform(co2_input))[0]
            )
        else:
            predicted_co2 = baseline_co2 * 0.9

        reduction = baseline_co2 - predicted_co2
        reduction_percent = (reduction / baseline_co2) * 100

        # ---------------- FILTERING ----------------

        base = materials.drop_duplicates(
            subset=["material_name"]
        ).copy()

        strict = base[
            (base["weight_capacity"] >= weight_capacity) &
            (base["strength"] >= strength - 1)
        ]

        relaxed = base[
            (base["weight_capacity"] >= weight_capacity * 0.7) &
            (base["strength"] >= strength - 2)
        ]

        if not strict.empty:
            filtered = strict
            logger.info("Using strict constraints")

        elif not relaxed.empty:
            filtered = relaxed
            logger.warning("Using relaxed constraints")

        else:
            filtered = base
            logger.error("No constraints matched — fallback to all materials")

        # ---------------- COST ----------------

        cost_scaled = scaler.transform(filtered[feature_cols])

        filtered["predicted_unit_cost"] = (
            cost_model.predict(cost_scaled)
            if use_cost_model
            else filtered["cost_per_unit"]
        )

        max_unit_cost = filtered["predicted_unit_cost"].quantile(
            max(0.1, min(cost_efficiency, 0.95))
        )

        filtered = filtered[
            filtered["predicted_unit_cost"] <= max_unit_cost
        ]

        # ---------------- NORMALIZE COST ----------------

        cmin = filtered["predicted_unit_cost"].min()
        cmax = filtered["predicted_unit_cost"].max()

        filtered["predicted_unit_cost_norm"] = (
            (filtered["predicted_unit_cost"] - cmin) /
            (cmax - cmin + 1e-6)
        )

        # ---------------- SCORE ----------------

        filtered["ai_recommendation_score"] = (

            (10 - abs(filtered["strength"] - strength)) * 0.25 +

            (10 - abs(filtered["weight_capacity"] - weight_capacity)) * 0.20 +

            filtered["biodegradability_score"] * 0.20 +

            filtered["recyclability_percent"] / 10 * 0.15 +

            (1 - filtered["predicted_unit_cost_norm"]) *
            (0.20 + cost_efficiency)
        )

        # ---------------- TOTAL COST ----------------

        filtered["total_cost"] = (
            filtered["predicted_unit_cost"] * quantity
        )

        top_materials = filtered.sort_values(
            by="ai_recommendation_score",
            ascending=False
        ).head(5)

        # ---------------- RESPONSE ----------------

        return jsonify({

            "product_name": product_name,
            "quantity": quantity,

            "baseline_co2": baseline_co2,
            "predicted_co2": round(predicted_co2, 2),
            "co2_reduction": round(reduction, 2),
            "co2_reduction_percent": round(reduction_percent, 2),

            "recommendation_strategy": "AI optimized sustainability and cost",

            "recommendations": top_materials[
                [
                    "material_name",
                    "predicted_unit_cost",
                    "total_cost",
                    "ai_recommendation_score"
                ]
            ].round(2).to_dict(orient="records")
        })

    except Exception as e:

        logger.exception("Recommendation API crashed")

        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500



# RUN


if __name__ == "__main__":
    app.run(debug=True)

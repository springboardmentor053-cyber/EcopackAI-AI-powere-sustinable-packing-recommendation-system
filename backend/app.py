import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv


# LOAD ENV VARIABLES

load_dotenv()

DATASET_PATH = os.getenv("DATASET_PATH")
CO2_MODEL_PATH = os.getenv("CO2_MODEL_PATH")
COST_MODEL_PATH = os.getenv("COST_MODEL_PATH")
LOG_FILE = os.getenv("LOG_FILE", "ecopackai.log")

os.makedirs("logs", exist_ok=True)


# LOGGING SETUP


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EcoPackAI")


# APP SETUP


app = Flask(__name__)
CORS(app)


# LOAD DATASET


try:
    materials = pd.read_csv(DATASET_PATH)
    materials["material_name"] = materials["material_name"].str.strip()
    logger.info("Dataset loaded successfully")
except Exception as e:
    logger.critical(f"Dataset load failed: {e}")
    raise


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
        "co2_model_loaded": use_co2_model,
        "cost_model_loaded": use_cost_model
    })


# VALIDATION HELPER


def validate_inputs(data, required):

    if not data:
        return "No input JSON provided"

    for field in required:
        if field not in data:
            return f"Missing field: {field}"

    try:
        if int(data["quantity"]) <= 0:
            return "Quantity must be greater than zero"

        if float(data["baseline_co2"]) <= 0:
            return "Baseline CO2 must be positive"

    except:
        return "Numeric values invalid"

    return None


# MAIN RECOMMENDATION API


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
            logger.warning(f"Validation failed: {error}")
            return jsonify({"error": error}), 400

        product_name = data.get("product_name", "Generic Product")
        selected_material = data.get("selected_material")
        quantity = int(data["quantity"])
        baseline_co2 = float(data["baseline_co2"])

        strength = float(data["strength_encoded"])
        weight_capacity = float(data["weight_capacity"])
        biodegradability = float(data["biodegradability_score"])
        recyclability = float(data["recyclability_percent"])
        cost_efficiency = float(data["cost_efficiency_score"])

        if selected_material:
            selected_material = selected_material.strip().lower()

        logger.info(f"Recommendation requested for {product_name}")

        #  CO2 PREDICTION 

        if use_co2_model:
            co2_input = pd.DataFrame([{
                "strength": strength,
                "weight_capacity": weight_capacity,
                "durability_score": 5,
                "biodegradability_score": biodegradability,
                "recyclability_percent": recyclability
            }])

            co2_scaled = scaler.transform(co2_input)
            predicted_co2 = float(co2_model.predict(co2_scaled)[0])
        else:
            predicted_co2 = baseline_co2 * 0.9

        #  CO2 REDUCTION 

        reduction = baseline_co2 - predicted_co2
        reduction_percent = (reduction / baseline_co2) * 100

        #  FILTER MATERIALS 

        filtered = materials.drop_duplicates(
            subset=["material_name"]
        ).copy()

        #  COST PREDICTION 

        if use_cost_model:

            cost_scaled = scaler.transform(
                filtered[feature_cols]
            )

            filtered["predicted_unit_cost"] = (
                cost_model.predict(cost_scaled)
            )

            max_unit_cost = filtered["predicted_unit_cost"].max()

        else:

            filtered["predicted_unit_cost"] = (
                filtered["cost_per_unit"]
            )

            max_unit_cost = cost_efficiency * 100

        #  BUDGET CONSTRAINT 

        filtered = filtered[
            filtered["predicted_unit_cost"] <= max_unit_cost
        ]

        #  EXCLUDE SELECTED MATERIAL 

        if selected_material:
            filtered = filtered[
                filtered["material_name"]
                .str.lower() != selected_material
            ]
            strategy = "Optimized alternatives to selected material"
        else:
            strategy = "Optimized based on product requirements"

        #  AI SCORING 

        filtered["ai_recommendation_score"] = (
            (10 - abs(filtered["strength"] - strength)) * 0.30 +
            (10 - abs(filtered["biodegradability_score"] - biodegradability)) * 0.25 +
            (10 - abs(filtered["recyclability_percent"] - recyclability) / 10) * 0.20 +
            (10 - filtered["predicted_unit_cost"]) * 0.25
        )

        #  COST TOTAL 

        filtered["total_cost"] = (
            filtered["predicted_unit_cost"] * quantity
        )

        #  RANKING 

        top_materials = filtered.sort_values(
            by="ai_recommendation_score",
            ascending=False
        ).head(5)

        logger.info("Top materials ranked successfully")

        #  RESPONSE 

        return jsonify({

            "product_name": product_name,
            "quantity": quantity,

            "baseline_co2": baseline_co2,
            "predicted_co2": round(predicted_co2, 2),
            "co2_reduction": round(reduction, 2),
            "co2_reduction_percent": round(reduction_percent, 2),

            "recommendation_strategy": strategy,

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



# RUN APP


if __name__ == "__main__":
    app.run(debug=True)

import os
import io
import logging
import pandas as pd
import joblib

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from sklearn.preprocessing import StandardScaler

from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# LOAD ENV


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

CO2_MODEL_PATH = os.getenv("CO2_MODEL_PATH")
COST_MODEL_PATH = os.getenv("COST_MODEL_PATH")

LOG_FILE = os.getenv("LOG_FILE", "logs/ecopackai.log")
os.makedirs("logs", exist_ok=True)

ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{ENCODED_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)

logger = logging.getLogger("EcoPackAI")


# APP


app = Flask(__name__)
CORS(app)


# LOAD DATA FROM POSTGRES


engine = create_engine(DATABASE_URL)

df = pd.read_sql("SELECT * FROM materials", engine)
df["material_name"] = df["material_name"].str.strip()

logger.info("Materials loaded from PostgreSQL")


# FEATURES


feature_cols = [
    "strength",
    "weight_capacity",
    "durability_score",
    "biodegradability_score",
    "recyclability_percent",
]

scaler = StandardScaler()
scaler.fit(df[feature_cols])


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


# HEALTH


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "EcoPackAI backend running",
        "co2_model_loaded": use_co2_model,
        "cost_model_loaded": use_cost_model,
    })


# RECOMMEND API


@app.route("/recommend", methods=["POST"])
def recommend_material():

    try:
        data = request.json

        quantity = int(data["quantity"])
        baseline_co2 = float(data["baseline_co2"])

        strength = float(data["strength_encoded"])
        weight = float(data["weight_capacity"])
        biodeg = float(data["biodegradability_score"])
        recycle = float(data["recyclability_percent"])
        cost_eff = float(data["cost_efficiency_score"])

        product_name = data.get("product_name", "Product")

        logger.info(
            f"Inputs: strength={strength}, weight={weight}, "
            f"bio={biodeg}, recycle={recycle}, cost_eff={cost_eff}"
        )

        
        # CO2 PREDICT
        

        if use_co2_model:
            X = pd.DataFrame([{
                "strength": strength,
                "weight_capacity": weight,
                "durability_score": 5,
                "biodegradability_score": biodeg,
                "recyclability_percent": recycle,
            }])

            predicted_co2 = float(co2_model.predict(scaler.transform(X))[0])
        else:
            predicted_co2 = baseline_co2 * 0.85

        reduction = baseline_co2 - predicted_co2
        reduction_pct = (reduction / baseline_co2) * 100

        
        # FILTER + SCORE
        

        working = df.copy()

        if len(working) == 0:
            return jsonify({"error": "No materials in database"}), 400

        if use_cost_model:
            cost_scaled = scaler.transform(working[feature_cols])
            working["predicted_unit_cost"] = cost_model.predict(cost_scaled)
        else:
            working["predicted_unit_cost"] = working["cost_per_unit"]

        # Soft budget control
        max_cost = working["predicted_unit_cost"].quantile(0.9)

        working = working[working["predicted_unit_cost"] <= max_cost]

        if len(working) == 0:
            working = df.copy()

        working["ai_recommendation_score"] = (
            (10 - abs(working["strength"] - strength)) * 0.30
            + (10 - abs(working["biodegradability_score"] - biodeg)) * 0.25
            + (10 - abs(working["recyclability_percent"] - recycle) / 10) * 0.20
            + (10 - working["predicted_unit_cost"]) * 0.25
        )

        working["total_cost"] = working["predicted_unit_cost"] * quantity

        top = working.sort_values(
            by="ai_recommendation_score",
            ascending=False,
        ).head(5)

        return jsonify({

            "product_name": product_name,
            "quantity": quantity,

            "baseline_co2": baseline_co2,
            "predicted_co2": round(predicted_co2, 2),
            "co2_reduction": round(reduction, 2),
            "co2_reduction_percent": round(reduction_pct, 2),

            "recommendations": top[
                [
                    "material_name",
                    "predicted_unit_cost",
                    "total_cost",
                    "ai_recommendation_score",
                ]
            ].round(2).to_dict(orient="records"),
        })

    except Exception as e:
        logger.exception("Recommendation crashed")
        return jsonify({"error": str(e)}), 500


# EXPORT CSV


@app.route("/export/csv", methods=["POST"])
def export_csv():

    recs = request.json["recommendations"]

    df = pd.DataFrame(recs)

    mem = io.BytesIO()
    df.to_csv(mem, index=False)
    mem.seek(0)

    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="ecopackai_report.csv",
    )


# EXPORT PDF


@app.route("/export/pdf", methods=["POST"])
def export_pdf():

    payload = request.json
    recs = payload["recommendations"]

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("EcoPackAI Sustainability Report", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        f"""
        Product: {payload['product_name']}<br/>
        Quantity: {payload['quantity']}<br/>
        Baseline CO₂: {payload['baseline_co2']}<br/>
        Predicted CO₂: {payload['predicted_co2']}<br/>
        Reduction %: {payload['co2_reduction_percent']}%
        """,
        styles["Normal"],
    ))

    story.append(Spacer(1, 20))

    table_data = [["Material", "Unit Cost", "Total Cost", "AI Score"]]

    for r in recs:
        table_data.append([
            r["material_name"],
            r["predicted_unit_cost"],
            r["total_cost"],
            r["ai_recommendation_score"],
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
    ]))

    story.append(table)

    doc.build(story)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="ecopackai_report.pdf",
    )


# RUN


if __name__ == "__main__":
    app.run(debug=True)

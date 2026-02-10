import os
import io
import logging
import pandas as pd
import joblib

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from urllib.parse import quote_plus

from sklearn.preprocessing import StandardScaler

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


# ENV 

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
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("EcoPackAI")


# APP 

app = Flask(__name__)
CORS(app)


# DATABASE 

engine = create_engine(DATABASE_URL)
logger.info("CONNECTED DATABASE")

materials_df = pd.read_sql("SELECT * FROM materials", engine)
materials_df["material_name"] = materials_df["material_name"].str.strip()

logger.info("Materials loaded")


# FEATURES 

feature_cols = [
    "strength",
    "weight_capacity",
    "durability_score",
    "biodegradability_score",
    "recyclability_percent",
]

scaler = StandardScaler()
scaler.fit(materials_df[feature_cols])


# MODELS 

def load_model(path, name):
    try:
        model = joblib.load(path)
        logger.info(f"{name} model loaded")
        return model, True
    except Exception:
        logger.warning(f"{name} model not found — fallback used")
        return None, False


co2_model, use_co2_model = load_model(CO2_MODEL_PATH, "CO2")
cost_model, use_cost_model = load_model(COST_MODEL_PATH, "Cost")


# HEALTH 

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "EcoPackAI backend running",
        "co2_model_loaded": use_co2_model,
        "cost_model_loaded": use_cost_model,
    })


# RECOMMEND 

@app.route("/recommend", methods=["POST"])
def recommend():

    try:
        data = request.json

        quantity = int(data["quantity"])
        if quantity <= 0:
            return jsonify({"error": "Quantity must be > 0"}), 400

        baseline_co2 = float(data["baseline_co2"])

        strength = float(data["strength_encoded"])
        weight = float(data["weight_capacity"])
        biodeg = float(data["biodegradability_score"])
        recycle = float(data["recyclability_percent"])

        product_name = data.get("product_name", "Product")

        #  CO2 

        if use_co2_model:
            X = pd.DataFrame([{
                "strength": strength,
                "weight_capacity": weight,
                "durability_score": 5,
                "biodegradability_score": biodeg,
                "recyclability_percent": recycle,
            }])

            predicted_co2 = float(
                co2_model.predict(scaler.transform(X))[0]
            )
        else:
            predicted_co2 = baseline_co2 * 0.85

        reduction = baseline_co2 - predicted_co2
        reduction_pct = (reduction / baseline_co2) * 100


        #  COST 

        working = materials_df.copy()

        if use_cost_model:
            scaled = scaler.transform(working[feature_cols])
            working["predicted_unit_cost"] = cost_model.predict(scaled)
        else:
            working["predicted_unit_cost"] = working["cost_per_unit"]

        cost_min = working["predicted_unit_cost"].min()
        cost_max = working["predicted_unit_cost"].max()

        if cost_max == cost_min:
            working["cost_score"] = 5
        else:
            working["cost_score"] = (
                10
                - ((working["predicted_unit_cost"] - cost_min)
                   / (cost_max - cost_min)) * 10
            )

        #  AI SCORE 

        working["ai_recommendation_score"] = (
            (10 - abs(working["strength"] - strength)) * 0.30
            + (10 - abs(working["biodegradability_score"] - biodeg)) * 0.25
            + (10 - abs(working["recyclability_percent"] - recycle) / 10) * 0.20
            + working["cost_score"] * 0.25
        )

        working["total_cost"] = working["predicted_unit_cost"] * quantity

        top = working.sort_values(
            by="ai_recommendation_score",
            ascending=False,
        ).head(5)

        top_row = top.iloc[0]

        # SAVE HISTORY 

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO analysis_history (
                        product_name,
                        quantity,
                        baseline_co2,
                        predicted_co2,
                        co2_reduction,
                        co2_reduction_percent,
                        top_material,
                        unit_cost,
                        total_cost,
                        ai_score
                    )
                    VALUES (:p, :q, :b, :pc, :r, :rp, :tm, :uc, :tc, :as)
                """),
                {
                    "p": product_name,
                    "q": quantity,
                    "b": baseline_co2,
                    "pc": predicted_co2,
                    "r": reduction,
                    "rp": reduction_pct,
                    "tm": top_row["material_name"],
                    "uc": float(top_row["predicted_unit_cost"]),
                    "tc": float(top_row["total_cost"]),
                    "as": float(top_row["ai_recommendation_score"]),
                }
            )

            for _, row in top.iterrows():
                conn.execute(
                    text("""
                        INSERT INTO usage_logs
                        (material_name, quantity)
                        VALUES (:m, :q)
                    """),
                    {"m": row["material_name"], "q": quantity},
                )

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
        logger.exception("Recommendation failed")
        return jsonify({"error": str(e)}), 500


# HISTORY 

@app.route("/history", methods=["GET"])
def history():

    try:
        df = pd.read_sql("""
            SELECT *
            FROM analysis_history
            ORDER BY created_at DESC
            LIMIT 100;
        """, engine)

        df = df.replace(
            [float("nan"), float("inf"), -float("inf")],
            None,
        )

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        logger.exception("History failed")
        return jsonify({"error": str(e)}), 500


# HISTORY COMPARE 

@app.route("/history/compare", methods=["GET"])
def compare_history():

    try:
        ids = request.args.getlist("id")

        if len(ids) != 2:
            return jsonify({"error": "Two IDs required"}), 400

        df = pd.read_sql("""
            SELECT *
            FROM analysis_history
            WHERE id = %s OR id = %s;
        """, engine, params=(ids[0], ids[1]))

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        logger.exception("Compare failed")
        return jsonify({"error": str(e)}), 500


# ANALYTICS 

@app.route("/analytics/usage")
def analytics_usage():

    df = pd.read_sql("""
        SELECT
            material_name,
            SUM(quantity) AS total_quantity,
            COUNT(*) AS times_recommended
        FROM usage_logs
        GROUP BY material_name
        ORDER BY total_quantity DESC;
    """, engine)

    return jsonify(df.to_dict(orient="records"))


# EXPORT CSV 

@app.route("/export/csv", methods=["POST"])
def export_csv():

    payload = request.json
    recs = payload.get("recommendations", [])

    df = pd.DataFrame(recs)

    summary = pd.DataFrame([{
        "Product": payload.get("product_name"),
        "Quantity": payload.get("quantity"),
        "Baseline CO2": payload.get("baseline_co2"),
        "Predicted CO2": payload.get("predicted_co2"),
        "CO2 Reduction": payload.get("co2_reduction"),
        "Reduction %": payload.get("co2_reduction_percent"),
    }])

    mem = io.BytesIO()
    summary.to_csv(mem, index=False)
    mem.write(b"\n")
    df.to_csv(mem, index=False)
    mem.seek(0)

    return send_file(mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="EcoPackAI_Report.csv"
    )


# EXPORT PDF 

@app.route("/export/pdf", methods=["POST"])
def export_pdf():

    payload = request.json
    recs = payload.get("recommendations", [])

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(
        "<b>EcoPackAI Recommendation Report</b>",
        styles["Title"]
    ))

    story.append(Spacer(1, 20))

    summary_data = [
        ["Product", payload.get("product_name")],
        ["Quantity", payload.get("quantity")],
        ["Baseline CO2", payload.get("baseline_co2")],
        ["Predicted CO2", payload.get("predicted_co2")],
        ["CO2 Reduction", payload.get("co2_reduction")],
        ["Reduction %", payload.get("co2_reduction_percent")],
    ]

    table = Table(summary_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    rec_table = [["Material","Unit Cost","Total Cost","AI Score"]]

    for r in recs:
        rec_table.append([
            r["material_name"],
            r["predicted_unit_cost"],
            r["total_cost"],
            r["ai_recommendation_score"],
        ])

    table2 = Table(rec_table)
    table2.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
    ]))

    story.append(table2)

    buf = io.BytesIO()

    doc = SimpleDocTemplate(buf, pagesize=A4)
    doc.build(story)

    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="EcoPackAI_Report.pdf",
    )


# RUN 

if __name__ == "__main__":
    app.run(debug=True)

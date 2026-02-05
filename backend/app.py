import json
import os

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
from services.recommendation_service import run_recommendation

from db import (
    ProductRequest,
    Recommendation,
    db_available,
    get_session,
    init_db,
)

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

CORS(app)

API_KEY = os.getenv("API_KEY")
DB_ENABLED = init_db()


def make_response(data=None, message="", status="success", http_status=200):
    payload = {
        "status": status,
        "message": message,
        "data": data,
    }
    return jsonify(payload), http_status


@app.before_request
def require_api_key():
    if not request.path.startswith("/api/"):
        return None

    if request.path == "/api/health":
        return None

    if not API_KEY:
        return None

    provided = request.headers.get("X-API-Key")
    if provided != API_KEY:
        return make_response(
            data=None,
            message="Unauthorized",
            status="error",
            http_status=401,
        )

    return None

@app.route("/health", methods=["GET"])
def health():
    return make_response(
        data={
            "status": "EcoPackAI backend running",
            "db_connected": DB_ENABLED,
        },
        message="OK",
    )


@app.route("/api/health", methods=["GET"])
def api_health():
    return make_response(
        data={
            "status": "EcoPackAI backend running",
            "db_connected": DB_ENABLED,
        },
        message="OK",
    )

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json

        if not data:
            return make_response(
                data=None,
                message="No input data provided",
                status="error",
                http_status=400,
            )

        df = pd.DataFrame(data)

        result = run_recommendation(df)

        if DB_ENABLED and db_available():
            session = get_session()
            if session:
                try:
                    payload = data[0] if isinstance(data, list) else data
                    request_row = ProductRequest(
                        strength=float(payload.get("strength")),
                        weight_capacity=float(payload.get("weight_capacity")),
                        biodegradability_score=float(payload.get("biodegradability_score")),
                        recyclability_percentage=float(payload.get("recyclability_percentage")),
                        fragility_level=float(payload.get("fragility_level")),
                        shipping_type=str(payload.get("shipping_type")),
                        raw_payload=json.dumps(payload),
                    )
                    session.add(request_row)
                    session.flush()

                    for _, row in result.iterrows():
                        rec = Recommendation(
                            request_id=request_row.id,
                            material_type=row["material_type"],
                            predicted_cost=float(row["predicted_cost"]),
                            predicted_co2=float(row["predicted_co2"]),
                            environmental_score=float(row["environmental_score"]),
                            rank_score=float(row["rank_score"]),
                        )
                        session.add(rec)

                    session.commit()
                except Exception:
                    session.rollback()
                finally:
                    session.close()

        return make_response(
            data=result.to_dict(orient="records"),
            message="Recommendations generated",
        )

    except Exception as e:
        return make_response(
            data=None,
            message=str(e),
            status="error",
            http_status=500,
        )


@app.route("/api/environment-score", methods=["POST"])
def environment_score():
    try:
        data = request.json

        if not data:
            return make_response(
                data=None,
                message="No input data provided",
                status="error",
                http_status=400,
            )

        df = pd.DataFrame(data)
        result = run_recommendation(df)

        payload = result[["material_type", "predicted_co2", "environmental_score"]]

        return make_response(
            data=payload.to_dict(orient="records"),
            message="Environmental scores computed",
        )

    except Exception as e:
        return make_response(
            data=None,
            message=str(e),
            status="error",
            http_status=500,
        )

if __name__ == "__main__":
    app.run(debug=True)

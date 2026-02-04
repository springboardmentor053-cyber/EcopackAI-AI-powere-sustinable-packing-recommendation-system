from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from services.recommendation_service import run_recommendation

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "EcoPackAI backend running"})


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json
    df = pd.DataFrame(data)

    result = run_recommendation(df)

    return jsonify(result.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)

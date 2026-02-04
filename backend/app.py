from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
from services.recommendation_service import run_recommendation

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "EcoPackAI backend running"})

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        df = pd.DataFrame(data)

        result = run_recommendation(df)

        return jsonify(result.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

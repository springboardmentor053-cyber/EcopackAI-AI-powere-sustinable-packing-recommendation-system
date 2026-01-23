from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd

app = Flask(__name__)


cost_model = joblib.load("E:/Data Science/EcoPackAI/models/cost_model_clean.pkl")
co2_model = joblib.load("E:/Data Science/EcoPackAI/models/cost_model_clean.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    input_df = pd.DataFrame([data])

    predicted_cost = cost_model.predict(input_df)[0]
    predicted_co2 = co2_model.predict(input_df)[0]

    return jsonify({
        "predicted_cost": float(predicted_cost),
        "predicted_co2": float(predicted_co2)
    })

if __name__ == "__main__":
    app.run(debug=True)

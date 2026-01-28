from flask import Flask, request, render_template
import numpy as np
import pickle

app = Flask(__name__)

# Load models
co2_model = pickle.load(open("co2_model.pkl", "rb"))
cost_model = pickle.load(open("cost_model.pkl", "rb"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Get input values from form
    float_features = [float(x) for x in request.form.values()]
    features = np.array([float_features])

    # Predictions
    co2_prediction = co2_model.predict(features)[0]
    cost_prediction = cost_model.predict(features)[0]

    return render_template(
        "index.html",
        co2_text=f"Predicted CO₂ Emission: {co2_prediction}",
        cost_text=f"Predicted Cost: ₹ {cost_prediction}"
    )

if __name__ == "__main__":
    app.run(debug=True)

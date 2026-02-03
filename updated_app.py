from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import psycopg2

app = Flask(__name__)

# Load ML models
co2_model = joblib.load("co2_model.pkl")
cost_model = joblib.load("cost_model.pkl")

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        dbname="Eco_Pack",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    product = request.get_json()

    required_fields = [
        "strength_score",
        "weight_capacity_kg",
        "biodegradability_score",
        "recyclability_percent",
        "moisture_resistance",
        "heat_resistance"
    ]

    # Validate inputs
    for field in required_fields:
        if field not in product:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Extract inputs
    strength_score = product["strength_score"]
    weight_capacity_kg = product["weight_capacity_kg"]
    biodegradability_score = product["biodegradability_score"]
    recyclability_percent = product["recyclability_percent"]
    moisture_resistance = product["moisture_resistance"]
    heat_resistance = product["heat_resistance"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch materials from DB
    cur.execute("""
    SELECT
        material_name,
        strength_score,
        weight_capacity_kg,
        biodegradability_score,
        recyclability_percent,
        moisture_resistance,
        heat_resistance
    FROM materials
    LIMIT 50;
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return jsonify({"error": "No materials found in database"}), 404

    results = []

    # Function to convert textual levels to numeric values
    def level_to_num(val):
        return {"Low": 3, "Medium": 6, "High": 9}.get(val, val)

    # Predict CO2 and Cost for each material
    for row in rows:
        features = np.array([[ 
            level_to_num(row[1]),  # strength_score
            row[2],                 # weight_capacity_kg
            level_to_num(row[3]),   # biodegradability_score
            row[4],                 # recyclability_percent
            level_to_num(row[5]),   # moisture_resistance
            level_to_num(row[6])    # heat_resistance
        ]])

        co2 = co2_model.predict(features)[0]
        cost = cost_model.predict(features)[0]

        # Filter based on product requirements
        if (
            level_to_num(row[1]) >= strength_score and
            row[2] >= weight_capacity_kg and
            level_to_num(row[3]) >= biodegradability_score and
            row[4] >= recyclability_percent and
            level_to_num(row[5]) >= moisture_resistance and
            level_to_num(row[6]) >= heat_resistance
        ):
            results.append({
                "material": row[0],
                "predicted_co2": round(co2, 2),
                "predicted_cost": round(cost, 2)
            })

    if not results:
        return jsonify({"error": "No suitable materials found"}), 404

    # Compute eco-score
    max_cost = max(r["predicted_cost"] for r in results)
    max_co2 = max(r["predicted_co2"] for r in results)

    for r in results:
        r["eco_score"] = round(
            (r["predicted_cost"] / max_cost) +
            (r["predicted_co2"] / max_co2),
            3
        )

    ranked = sorted(results, key=lambda x: x["eco_score"])[:5]

    return jsonify({"recommended_materials": ranked})

if __name__ == "__main__":
    app.run(debug=True)

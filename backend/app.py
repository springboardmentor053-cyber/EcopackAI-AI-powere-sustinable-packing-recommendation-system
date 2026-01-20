from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

# ================================
# Flask App Setup
# ================================
app = Flask(__name__)
CORS(app)

# ================================
# Load ML Models
# ================================
cost_model = joblib.load(
    r"D:/Project ecopackai/backend/models/cost_prediction_model.pkl"
)

co2_model = joblib.load(
    r"D:/Project ecopackai/backend/models/co2_prediction_model.pkl"
)

# ================================
# Load Dataset
# ================================
materials = pd.read_csv(
    r"D:/Project ecopackai/data/materials_module2_final.csv"
)

# ================================
# Feature Columns (ML)
# ================================
feature_cols = [
    "strength",
    "weight_capacity",
    "durability_score",
    "biodegradability_score",
    "recyclability_percent"
]

# ================================
# Scaler
# ================================
scaler = StandardScaler()
scaler.fit(materials[feature_cols])

# ================================
# Health Check
# ================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "EcoPackAI backend running (All-Rounder Mode)"})

# ================================
# Recommendation API
# ================================
@app.route("/recommend", methods=["POST"])
def recommend_material():
    data = request.json

    # ----------------------------
    # User Inputs
    # ----------------------------
    product_name = data.get("product_name", "Generic Product")
    quantity = int(data.get("quantity", 1))

    strength = float(data["strength_encoded"])
    weight_capacity = float(data["weight_capacity"])
    biodegradability = float(data["biodegradability_score"])
    recyclability = float(data["recyclability_percent"])
    cost_efficiency = float(data["cost_efficiency_score"])

    # ----------------------------
    # ML Input (Product-level)
    # ----------------------------
    user_input = pd.DataFrame([{
        "strength": strength,
        "weight_capacity": weight_capacity,
        "durability_score": 5,
        "biodegradability_score": biodegradability,
        "recyclability_percent": recyclability
    }])

    user_scaled = scaler.transform(user_input)

    predicted_co2 = float(co2_model.predict(user_scaled)[0])

    # ----------------------------
    # Budget Constraint
    # ----------------------------
    max_unit_cost_allowed = cost_efficiency * 100

    filtered = materials[
        materials["cost_per_unit"] <= max_unit_cost_allowed
    ].copy()

    # Remove duplicate material names
    filtered = filtered.drop_duplicates(subset=["material_name"])

    # ----------------------------
    # Material-Specific Costs
    # ----------------------------
    filtered["predicted_unit_cost"] = filtered["cost_per_unit"]
    filtered["total_cost"] = filtered["predicted_unit_cost"] * quantity

    # ----------------------------
    # HYBRID AI RECOMMENDATION SCORE ⭐
    # ----------------------------
    filtered["ai_recommendation_score"] = (
    (10 - abs(filtered["strength"] - strength)) * 0.3 +
    (10 - abs(filtered["biodegradability_score"] - biodegradability)) * 0.25 +
    (10 - abs(filtered["recyclability_percent"] - recyclability) / 10) * 0.2 +
    (10 - filtered["cost_per_unit"]) * 0.25
    )


    # ----------------------------
    # Rule-Based Intelligence (All-Rounder)
    # ----------------------------
    if strength >= 8:
        filtered["ai_recommendation_score"] += filtered["strength"] * 0.2

    if biodegradability >= 8:
        filtered["ai_recommendation_score"] += filtered["biodegradability_score"] * 0.2

    # ----------------------------
    # Final Ranking
    # ----------------------------
    top_materials = filtered.sort_values(
        by="ai_recommendation_score",
        ascending=False
    ).head(5)

    # ----------------------------
    # Response
    # ----------------------------
    return jsonify({
        "product_name": product_name,
        "quantity": quantity,
        "predicted_co2": round(predicted_co2, 2),
        "note": "Recommendations optimized using hybrid AI (ML + sustainability + cost rules)",
        "recommendations": top_materials[
            [
                "material_name",
                "predicted_unit_cost",
                "total_cost",
                "ai_recommendation_score"
            ]
        ].round(2).to_dict(orient="records")
    })

# ================================
# Run Server
# ================================
if __name__ == "__main__":
    app.run(debug=True)

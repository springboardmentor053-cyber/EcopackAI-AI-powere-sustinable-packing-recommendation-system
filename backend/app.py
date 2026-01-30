from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

# ================================
# App Setup
# ================================
app = Flask(__name__)
CORS(app)

# ================================
# Load Dataset
# ================================
materials = pd.read_csv(
    r"D:/Project ecopackai/data/materials_module2_final.csv"
)

materials["material_name"] = materials["material_name"].str.strip()

# ================================
# Feature Columns
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
# Load ML Models
# ================================
try:
    co2_model = joblib.load(
        r"D:/Project ecopackai/backend/models/co2_prediction_model.pkl"
    )
    use_co2_model = True
except Exception as e:
    print("❌ CO2 model load failed:", e)
    use_co2_model = False

try:
    cost_model = joblib.load(
        r"D:/Project ecopackai/backend/models/cost_prediction_model.pkl"
    )
    use_cost_model = True
except Exception as e:
    print("❌ Cost model load failed:", e)
    use_cost_model = False

print("✅ CO2 model loaded:", use_co2_model)
print("✅ Cost model loaded:", use_cost_model)

# ================================
# Health Check
# ================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "EcoPackAI backend running",
        "co2_model_loaded": use_co2_model,
        "cost_model_loaded": use_cost_model
    })

# ================================
# Recommendation API
# ================================
@app.route("/recommend", methods=["POST"])
def recommend_material():

    data = request.json

    # ----------------------------
    # Read Inputs
    # ----------------------------
    product_name = data.get("product_name", "Generic Product")
    selected_material = data.get("selected_material", None)
    quantity = int(data.get("quantity", 1))

    strength = float(data["strength_encoded"])
    weight_capacity = float(data["weight_capacity"])
    biodegradability = float(data["biodegradability_score"])
    recyclability = float(data["recyclability_percent"])
    cost_efficiency = float(data["cost_efficiency_score"])

    if selected_material:
        selected_material = selected_material.strip().lower()

    # ----------------------------
    # CO2 Prediction (PRODUCT LEVEL)
    # ----------------------------
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
        predicted_co2 = 5.0

    # ----------------------------
    # INITIAL FILTER SET
    # ----------------------------
    filtered = materials.copy()
    filtered = filtered.drop_duplicates(subset=["material_name"])

    # ----------------------------
    # Cost Prediction (PER MATERIAL)
    # ----------------------------
    if use_cost_model:

        cost_features = filtered[feature_cols].copy()
        cost_scaled = scaler.transform(cost_features)

        filtered["predicted_unit_cost"] = cost_model.predict(cost_scaled)

        max_unit_cost = filtered["predicted_unit_cost"].max()

    else:
        filtered["predicted_unit_cost"] = filtered["cost_per_unit"]
        max_unit_cost = cost_efficiency * 100

    # ----------------------------
    # Apply Budget Constraint
    # ----------------------------
    filtered = filtered[
        filtered["predicted_unit_cost"] <= max_unit_cost
    ].copy()

    # ----------------------------
    # Exclude Selected Material
    # ----------------------------
    if selected_material:
        filtered = filtered[
            filtered["material_name"].str.lower().str.strip()
            != selected_material
        ]
        strategy = "Optimized alternatives based on selected material"
    else:
        strategy = "Optimized based on product requirements"

    # ----------------------------
    # AI Scoring Logic
    # ----------------------------
    filtered["ai_recommendation_score"] = (
        (10 - abs(filtered["strength"] - strength)) * 0.30 +
        (10 - abs(filtered["biodegradability_score"] - biodegradability)) * 0.25 +
        (10 - abs(filtered["recyclability_percent"] - recyclability) / 10) * 0.20 +
        (10 - filtered["predicted_unit_cost"]) * 0.25
    )

    # ----------------------------
    # Cost Calculations
    # ----------------------------
    filtered["total_cost"] = filtered["predicted_unit_cost"] * quantity

    # ----------------------------
    # Ranking
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


# ================================
# Run App
# ================================
if __name__ == "__main__":
    app.run(debug=True)

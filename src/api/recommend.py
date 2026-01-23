from flask import Flask, request, jsonify
import pandas as pd
import joblib

# -------------------------------------------------
# App init
# -------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------
# Load datasets
# -------------------------------------------------
PRODUCTS_PATH = "E:/Data Science/EcoPackAI/data/processed/products_cleaned.csv"
MATERIALS_PATH = "E:/Data Science/EcoPackAI/data/processed/materials_featured.csv"

products_df = pd.read_csv(PRODUCTS_PATH)
materials_df = pd.read_csv(MATERIALS_PATH)

# Normalize product_id (VERY IMPORTANT)
products_df["product_id"] = (
    products_df["product_id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# -------------------------------------------------
# Load ML artifacts
# -------------------------------------------------
preprocessor = joblib.load(
    "E:/Data Science/EcoPackAI/models/preprocessor.pkl"
)
cost_model = joblib.load(
    "E:/Data Science/EcoPackAI/models/cost_model_clean.pkl"
)
co2_model = joblib.load(
    "E:/Data Science/EcoPackAI/models/co2_model_clean.pkl"
)

# -------------------------------------------------
# Helper functions
# -------------------------------------------------

def get_product(product_id: str) -> pd.Series:
    """
    Fetch product row by product_id
    """
    row = products_df.loc[products_df["product_id"] == product_id]
    if row.empty:
        raise ValueError("Invalid product_id")
    return row.iloc[0]


def filter_materials(materials: pd.DataFrame, product: pd.Series) -> pd.DataFrame:
    """
    Apply rule-based constraints BEFORE ML
    """

    filtered = materials.copy()

    # --- WEIGHT CONSTRAINT ---
    # product weight is in GRAMS
    product_weight_g = product["product_weight_g"]

    if pd.isna(product_weight_g):
        raise ValueError("Product weight missing")

    # Convert grams → kilograms
    product_weight_kg = product_weight_g / 1000.0

    filtered = filtered[
        filtered["weight_capacity"] >= product_weight_kg
    ]

    # --- FRAGILITY CONSTRAINT ---
    if product["fragility_level"] == "High":
        filtered = filtered[
            filtered["strength_mpa"] >= 20
        ]

    return filtered


def prepare_features(materials: pd.DataFrame) -> pd.DataFrame:
    """
    Select ML input features
    """
    return materials[
        [
            "strength_mpa",
            "weight_capacity",
            "biodegradability_score",
            "recyclability_pct",
            "material_category"
        ]
    ]


def rank_materials(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rank materials using predicted cost and CO2
    """
    df = df.copy()

    df["rank_cost"] = df["predicted_cost"].rank(
        ascending=True, method="average"
    )
    df["rank_co2"] = df["predicted_co2"].rank(
        ascending=True, method="average"
    )

    df["final_score"] = (
        0.5 * df["rank_cost"] +
        0.5 * df["rank_co2"]
    )

    return df.sort_values("final_score")


# -------------------------------------------------
# API Endpoint
# -------------------------------------------------

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json or {}

    # Normalize input product_id
    product_id = (
        data.get("product_id", "")
        .strip()
        .upper()
    )

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    try:
        # Step 1: fetch product
        product = get_product(product_id)

        # Step 2: rule-based filtering
        filtered_materials = filter_materials(
            materials_df, product
        )

        if filtered_materials.empty:
            return jsonify({
                "product_id": product_id,
                "product_name": product["product_name"],
                "message": "No suitable materials found"
            }), 200

        # Step 3: ML predictions
        X = prepare_features(filtered_materials)
        X_processed = preprocessor.transform(X)

        filtered_materials["predicted_cost"] = (
            cost_model.predict(X_processed)
        )
        filtered_materials["predicted_co2"] = (
            co2_model.predict(X_processed)
        )

        # Step 4: ranking
        ranked = rank_materials(filtered_materials)

        # Step 5: response
        output = ranked[
            [
                "material_type",
                "predicted_cost",
                "predicted_co2",
                "final_score"
            ]
        ].head(3)

        return jsonify({
            "product_id": product_id,
            "product_name": product["product_name"],
            "product_category": product["product_category"],
            "recommendations": output.to_dict(orient="records")
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# Run app
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
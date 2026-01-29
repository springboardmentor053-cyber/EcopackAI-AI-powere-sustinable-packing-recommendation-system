from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os


app = Flask(__name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "processed", "products_cleaned.csv")
MATERIALS_PATH = os.path.join(BASE_DIR, "data", "processed", "materials_featured.csv")

PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "preprocessor.pkl")
COST_MODEL_PATH = os.path.join(BASE_DIR, "models", "cost_model_clean.pkl")
CO2_MODEL_PATH = os.path.join(BASE_DIR, "models", "co2_model_clean.pkl")


products_df = pd.read_csv(PRODUCTS_PATH)
materials_df = pd.read_csv(MATERIALS_PATH)

products_df["product_id"] = (
    products_df["product_id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

preprocessor = joblib.load(PREPROCESSOR_PATH)
cost_model = joblib.load(COST_MODEL_PATH)
co2_model = joblib.load(CO2_MODEL_PATH)


def get_product(product_id: str) -> pd.Series:
    row = products_df.loc[products_df["product_id"] == product_id]
    if row.empty:
        raise ValueError("Invalid product_id")
    return row.iloc[0]


def filter_materials(materials: pd.DataFrame, product: pd.Series) -> pd.DataFrame:
    filtered = materials.copy()

    product_weight_g = product.get("product_weight_g", None)
    if pd.isna(product_weight_g):
        raise ValueError("Product weight missing")

    product_weight_kg = float(product_weight_g) / 1000.0

    filtered = filtered[filtered["weight_capacity"] >= product_weight_kg]

    if product.get("fragility_level", "") == "High":
        filtered = filtered[filtered["strength_mpa"] >= 20]

    return filtered


def prepare_features(materials: pd.DataFrame) -> pd.DataFrame:
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
    df = df.copy()

    df["rank_cost"] = df["predicted_cost"].rank(ascending=True, method="average")
    df["rank_co2"] = df["predicted_co2"].rank(ascending=True, method="average")

    df["final_score"] = (0.5 * df["rank_cost"]) + (0.5 * df["rank_co2"])

    return df.sort_values("final_score")


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json or {}

    product_id = str(data.get("product_id", "")).strip().upper()

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    try:
        product = get_product(product_id)

        filtered_materials = filter_materials(materials_df, product)

        if filtered_materials.empty:
            return jsonify({
                "product_id": product_id,
                "product_name": product.get("product_name", ""),
                "message": "No suitable materials found"
            }), 200

        X = prepare_features(filtered_materials)
        X_processed = preprocessor.transform(X)

        filtered_materials["predicted_cost"] = cost_model.predict(X_processed)
        filtered_materials["predicted_co2"] = co2_model.predict(X_processed)

        ranked = rank_materials(filtered_materials)

        top3 = ranked[
            ["material_type", "predicted_cost", "predicted_co2", "final_score"]
        ].head(3)

        return jsonify({
            "product_id": product_id,
            "product_name": product.get("product_name", ""),
            "product_category": product.get("product_category", ""),
            "recommendations": top3.to_dict(orient="records")
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

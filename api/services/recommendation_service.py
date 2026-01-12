import pandas as pd
from pathlib import Path
from joblib import load
from src.models.recommender import rank_materials

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = BASE_DIR / "models_artifacts"
DATA_PATH = BASE_DIR / "data" / "final" / "ml_dataset.csv"

cost_model = load(MODEL_PATH / "cost_model.pkl")
co2_model = load(MODEL_PATH / "co2_model.pkl")
scaler = load(MODEL_PATH / "scaler.pkl")
encoders = load(MODEL_PATH / "encoders.pkl")

CATEGORICAL_COLS = ["eco_alternative", "category"]
NUMERICAL_COLS = ["weight_capacity_upto"]

def preprocess_input(df):
    for col in CATEGORICAL_COLS:
        df[col] = encoders[col].transform(df[col])

    df[NUMERICAL_COLS] = scaler.transform(df[NUMERICAL_COLS])
    return df

def recommend_material(user_input, top_n=5):
    dataset = pd.read_csv(DATA_PATH)

    filtered = dataset[
        (dataset["category"] == user_input["category"]) &
        (dataset["weight_capacity_upto"] >= user_input["weight_capacity_upto"])
    ].copy()

    filtered_processed = preprocess_input(filtered)

    filtered["predicted_cost"] = cost_model.predict(filtered_processed)
    filtered["predicted_co2"] = co2_model.predict(filtered_processed)

    ranked = rank_materials(filtered, top_n)

    return ranked[
        [
            "eco_alternative",
            "category",
            "predicted_cost",
            "predicted_co2",
            "sustainability_score",
            "final_rank_score"
        ]
    ].to_dict(orient="records")

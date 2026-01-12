import sys
import pandas as pd
from pathlib import Path

# Add src directory to sys.path to allow imports from models, evaluation, etc.
# This fixes ModuleNotFoundError when running as 'python -m src.main'
sys.path.append(str(Path(__file__).resolve().parent))

from models.cost_model import train_cost_model
from models.co2_model import train_co2_model
from models.model_utils import create_scaler, create_label_encoder, save_artifact
from evaluation.metrics import regression_metrics

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "feature_engineered_materials.csv"
ARTIFACT_PATH = BASE_DIR / "models_artifacts"

TARGET_COST = "cost_per_unit_inr"
TARGET_CO2 = "co2_emission_score"

CATEGORICAL_COLS = ["material_type", "water_resistance"]
NUMERICAL_COLS = [
    "strength",
    "weight_capacity_kg",
    "biodegradability_score",
    "recyclability_percent"
]

df = pd.read_csv(DATA_PATH)

encoders = {}
for col in CATEGORICAL_COLS:
    le = create_label_encoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

scaler = create_scaler()
df[NUMERICAL_COLS] = scaler.fit_transform(df[NUMERICAL_COLS])

X = df[CATEGORICAL_COLS + NUMERICAL_COLS]
y_cost = df[TARGET_COST]
y_co2 = df[TARGET_CO2]

cost_model = train_cost_model(X, y_cost)
co2_model = train_co2_model(X, y_co2)

cost_pred = cost_model.predict(X)
co2_pred = co2_model.predict(X)

print("Cost Model Metrics:", regression_metrics(y_cost, cost_pred))
print("CO2 Model Metrics:", regression_metrics(y_co2, co2_pred))

ARTIFACT_PATH.mkdir(exist_ok=True)

save_artifact(cost_model, ARTIFACT_PATH / "cost_model.pkl")
save_artifact(co2_model, ARTIFACT_PATH / "co2_model.pkl")
save_artifact(scaler, ARTIFACT_PATH / "scaler.pkl")
save_artifact(encoders, ARTIFACT_PATH / "encoders.pkl")

print("ML TRAINING COMPLETED SUCCESSFULLY")

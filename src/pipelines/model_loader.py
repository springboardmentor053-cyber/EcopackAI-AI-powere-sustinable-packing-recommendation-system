import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # project root
MODELS_DIR = BASE_DIR / "E:/Data Science/EcoPackAI/models"

def load_models():
    co2_model = joblib.load(MODELS_DIR / "E:/Data Science/EcoPackAI/models/co2_model.pkl")
    cost_model = joblib.load(MODELS_DIR / "E:/Data Science/EcoPackAI/models/cost_model.pkl")  # MUST be fixed if failing
    return co2_model, cost_model

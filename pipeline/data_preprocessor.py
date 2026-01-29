import pandas as pd
import joblib
import os

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "materials_featured.csv")
SAVE_PATH = os.path.join(BASE_DIR, "models", "preprocessor.pkl")

materials = pd.read_csv(DATA_PATH)

features = ["strength_mpa", "weight_capacity", "biodegradability_score", "recyclability_pct", "material_category"]
X = materials[features]

num_cols = ["strength_mpa", "weight_capacity", "biodegradability_score", "recyclability_pct"]
cat_cols = ["material_category"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
    ]
)

preprocessor.fit(X)

joblib.dump(preprocessor, SAVE_PATH)

print("✅ preprocessor.pkl created successfully!")
print("Saved at:", SAVE_PATH)

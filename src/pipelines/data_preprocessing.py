import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

NUMERIC_FEATURES = [
    "strength_mpa",
    "weight_capacity",
    "biodegradability_score",
    "recyclability_pct"
]

CATEGORICAL_FEATURES = ["material_category"]

def load_data(path):
    return pd.read_csv(path)

def split_xy(df):
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_cost = df["cost_inr_per_kg"]
    y_co2 = df["co2_emission_per_kg"]
    return X, y_cost, y_co2

def build_preprocessor():
    num_pipe = Pipeline([("scaler", StandardScaler())])
    cat_pipe = Pipeline([("onehot", OneHotEncoder(handle_unknown="ignore"))])

    return ColumnTransformer([
        ("num", num_pipe, NUMERIC_FEATURES),
        ("cat", cat_pipe, CATEGORICAL_FEATURES)
    ])

def train_test(X, y, test_size=0.2, rs=42):
    return train_test_split(X, y, test_size=test_size, random_state=rs)
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


NUMERIC_FEATURES = [
    "strength_mpa",
    "weight_capacity",
    "recyclability_pct",
    "biodegradability_score"
]

CATEGORICAL_FEATURES = [
    "material_category"
]

TARGET_COST = "cost_inr_per_kg"
TARGET_CO2 = "co2_emission_kg_per_kg"

EXCLUDED_COLUMNS = [
    "cost_norm",
    "co2_norm",
    "co2_impact_index",
    "cost_efficiency_index",
    "material_suitability_score"
]

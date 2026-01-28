# ===============================
# 1. Imports
# ===============================
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


# ===============================
# 2. Load Dataset
# ===============================
df = pd.read_csv("module2_feature_engineered_materials.csv")

print(df.shape)
print(df.columns)


# ===============================
# 3. Feature & Target Selection
# ===============================
X = df[
    [
        "strength_score",
        "weight_capacity_score",
        "biodegradability_score",
        "recyclability_percent",
    ]
]

# Targets
y_cost = df["cost_score"]
y_co2 = df["co2_impact_index"]

print(X.shape, y_cost.shape, y_co2.shape)


# ===============================
# 4. Train-Test Split
# ===============================
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)

# Keep same indices for CO2 target
y_co2_train = y_co2.loc[y_cost_train.index]
y_co2_test = y_co2.loc[y_cost_test.index]

print(X_train.shape)
print(X_test.shape)


# ===============================
# 5. Train Cost Model
# ===============================
cost_model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)

cost_model.fit(X_train, y_cost_train)


# ===============================
# 6. Evaluate Cost Model
# ===============================
cost_predictions = cost_model.predict(X_test)

print("\nCOST MODEL EVALUATION")
print("MAE:", mean_absolute_error(y_cost_test, cost_predictions))
print("RMSE:", np.sqrt(mean_squared_error(y_cost_test, cost_predictions)))
print("R2:", r2_score(y_cost_test, cost_predictions))


# ===============================
# 7. Train CO2 Model
# ===============================
co2_model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)

co2_model.fit(X_train, y_co2_train)


# ===============================
# 8. Evaluate CO2 Model
# ===============================
co2_predictions = co2_model.predict(X_test)

print("\nCO2 MODEL EVALUATION")
print("MAE:", mean_absolute_error(y_co2_test, co2_predictions))
print("RMSE:", np.sqrt(mean_squared_error(y_co2_test, co2_predictions)))
print("R2:", r2_score(y_co2_test, co2_predictions))


# ===============================
# 9. Save Models
# ===============================
joblib.dump(cost_model, "cost_model.pkl")
joblib.dump(co2_model, "co2_model.pkl")

print("\nModels saved successfully.")


# ===============================
# 10. Final Ranking Score
# ===============================
df_test = df.loc[X_test.index].copy()

df_test["predicted_cost"] = cost_predictions
df_test["predicted_co2"] = co2_predictions

df_test["final_score"] = (
    0.5 * df_test["predicted_cost"].rank(ascending=True)
    + 0.5 * df_test["predicted_co2"].rank(ascending=True)
)

df_test_sorted = df_test.sort_values("final_score")

print("\nTop 5 Best Materials:")
print(df_test_sorted.head())

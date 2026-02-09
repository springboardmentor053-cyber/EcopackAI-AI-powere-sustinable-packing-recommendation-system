import pickle
import os

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

with open(os.path.join(data_folder, "rf_cost_model.pkl"), "rb") as f:
    rf_model = pickle.load(f)

with open(os.path.join(data_folder, "xgb_co2_model.pkl"), "rb") as f:
    xgb_model = pickle.load(f)

print("RF model loaded:", rf_model)
print("XGB model loaded:", xgb_model)

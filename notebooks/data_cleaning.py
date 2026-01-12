import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

input_file = os.path.join(RAW_DIR, "material data.xlsx")
output_file = os.path.join(PROCESSED_DIR, "cleaned_material_data.csv")

df = pd.read_excel(input_file)

df.drop_duplicates(inplace=True)
df.columns = df.columns.str.lower().str.replace(" ", "_")

os.makedirs(PROCESSED_DIR, exist_ok=True)

df.to_csv(output_file, index=False)

print("Material data cleaned successfully")

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

files = [
    "E-commerce.xlsx",
    "Shopping.xlsx",
    "Food Delivery & Takeaway.xlsx",
    "Cosmetics, FMCG & Personal Care.xlsx",
    "Electronics & Fragile Products.xlsx"
]

for file in files:
    file_path = os.path.join(RAW_DIR, file)
    df = pd.read_excel(file_path)

    df.drop_duplicates(inplace=True)
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    df["weight_capacity_upto"] = (
        df["weight_capacity_upto"]
        .astype(str)
        .str.replace(" kg", "")
        .astype(int)
    )

    output_dir = os.path.join(BASE_DIR, "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    output_name = file.lower().replace(" ", "_").replace("&", "and").replace(".xlsx", ".csv")
    df.to_csv(os.path.join(output_dir, f"cleaned_{output_name}"), index=False)

    print(f"{file} processed successfully")

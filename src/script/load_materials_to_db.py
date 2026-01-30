import pandas as pd
from src.utils.db import engine

CSV_PATH = "E:/Data Science/EcoPackAI/data/processed/materials_cleaned.csv"

df = pd.read_csv(CSV_PATH)

df.to_sql(
    "materials",
    engine,
    if_exists="replace",
    index=False
)

print("Materials loaded into PostgreSQL")
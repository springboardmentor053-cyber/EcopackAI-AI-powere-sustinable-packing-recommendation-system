import pandas as pd
import os
from sqlalchemy import create_engine

# Database connection
engine = create_engine(
    "postgresql://postgres:varshi123@localhost:5432/ecopackai_new"
)

# Load CSV files
categories = pd.read_csv(
    r"C:\Users\VARSHITHA\OneDrive\Desktop\eco-pack_ai\eco-pack-ai\data\raw\product_categories.csv"
)



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "materials.csv")

df = pd.read_csv(DATA_PATH)



# Insert into PostgreSQL
categories.to_sql(
    "product_categories",
    engine,
    if_exists="append",
    index=False
)

materials.to_sql(
    "materials",
    engine,
    if_exists="append",
    index=False
)

print("Data loaded successfully!")

import pandas as pd
from sqlalchemy import create_engine

# 🔗 PostgreSQL connection
engine = create_engine(
    "postgresql+psycopg2://postgres:1234@localhost:5432/ecopackai"
)

# 📥 Load data from PostgreSQL
products = pd.read_sql("SELECT * FROM products", engine)
materials = pd.read_sql("SELECT * FROM materials", engine)

# 🔍 Understand the data
print("=== PRODUCTS SAMPLE ===")
print(products.head())

print("\n=== PRODUCTS INFO ===")
print(products.info())

print("\n=== MATERIALS SAMPLE ===")
print(materials.head())

print("\n=== MATERIALS INFO ===")
print(materials.info())

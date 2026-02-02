from sqlalchemy import create_engine
import pandas as pd


DB_NAME = "ecopackai"
DB_USER = "postgres"
DB_PASSWORD = "1234"   
DB_HOST = "localhost"
DB_PORT = "5432"


engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


products_df = pd.read_sql("SELECT * FROM products;", engine)
materials_df = pd.read_sql("SELECT * FROM materials;", engine)


print("✅ Products table connected successfully")
print(products_df.head())

print("\n✅ Materials table connected successfully")
print(materials_df.head())

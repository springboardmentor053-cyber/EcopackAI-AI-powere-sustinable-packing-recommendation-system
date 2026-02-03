import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Load CSV
df = pd.read_csv(
    r"D:/Project ecopackai/data/materials_module2_final.csv"
)

# Create DB engine
engine = create_engine(DATABASE_URL)

# Upload to PostgreSQL
df.to_sql("materials", engine, if_exists="append", index=False)

print("✅ CSV imported into PostgreSQL successfully!")

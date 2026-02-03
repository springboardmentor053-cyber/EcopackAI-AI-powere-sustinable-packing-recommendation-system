import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:Esakki%402008@localhost:5432/ecopackai"
)


df = pd.read_csv(
    r"D:/Project ecopackai/data/materials_module2_final.csv"
)

df.columns = df.columns.str.strip()

df.to_sql("materials", engine, if_exists="append", index=False)

print("✅ CSV imported into PostgreSQL")

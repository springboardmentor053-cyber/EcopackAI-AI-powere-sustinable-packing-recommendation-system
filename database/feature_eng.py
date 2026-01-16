import pandas as pd
from sqlalchemy import create_engine, exc
import numpy as np

# ---------------- DATABASE CONFIG ----------------
DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecopackai_db"

def feature_engineering():
    try:
        # Create DB Engine
        connection_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_str)
        
        # ---------------- LOAD DATA FROM DB ----------------
        print("Connecting to database...")
        query = """
        SELECT
            material_id,
            material_type,
            strength,
            weight_capacity_kg,
            biodegradability_score,
            co2_emission_score,
            recyclability_percent,
            cost_per_unit_inr,
            water_resistance
        FROM public.materials;
        """
        
        try:
            df = pd.read_sql(query, engine)
        except exc.OperationalError:
            print("❌ Error: Could not connect to the database. Is it running?")
            return
        except exc.ProgrammingError as e:
            print(f"❌ Error: Could not query table 'materials'. Does it exist? ({e})")
            return
            
        if df.empty:
            print("❌ Warning: 'materials' table is empty. No features to engineer.")
            return

        print(f"Loaded {len(df)} rows from 'materials'.")

        # ---------------- FEATURE ENGINEERING ----------------

        # 1️⃣ CO₂ Impact Index (lower is better)
        df["co2_impact_index"] = df["co2_emission_score"] * df["weight_capacity_kg"]

        # 2️⃣ Cost Efficiency Index (higher is better)
        # Avoid division by zero
        df["cost_efficiency_index"] = df["strength"] / df["cost_per_unit_inr"].replace(0, np.nan)
        df["cost_efficiency_index"] = df["cost_efficiency_index"].fillna(0) # or suitable default

        # 3️⃣ Sustainability Score (combined metric)
        df["sustainability_score"] = (
            df["biodegradability_score"] * 0.4 +
            (df["recyclability_percent"] / 100) * 0.4 -
            df["co2_emission_score"] * 0.2
        )

        # 4️⃣ Final Material Suitability Score
        df["material_suitability_score"] = (
            df["cost_efficiency_index"] * 0.3 +
            df["sustainability_score"] * 0.5 +
            (df["water_resistance"] * 0.2)
        )

        # ---------------- SAVE ENGINEERED DATA ----------------
        print("Saving engineered features to 'features_engineering' table...")
        df.to_sql(
            name="features_engineering",
            con=engine,
            schema="public",
            if_exists="replace",
            index=False
        )

        print("✅ Feature engineering completed successfully")
        print("✅ New table created:")
        print("   ecopackai_db → Schemas → public → Tables → features_engineering")
        
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    feature_engineering()

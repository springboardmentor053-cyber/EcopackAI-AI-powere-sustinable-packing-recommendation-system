import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env_db file
# Root is one level up from data/
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(basedir, '.env_db'))

# Database connection parameters
DB_PARAMS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "ecopackai_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "port": os.getenv("DB_PORT", "5432")
}

def create_tables(cur):
    """Creates the necessary tables if they do not exist."""
    
    # DDL for materials table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            material_id INT PRIMARY KEY,
            material_type VARCHAR(255),
            strength INT,
            weight_capacity_kg INT,
            biodegradability_score INT,
            co2_emission_score FLOAT,
            recyclability_percent INT,
            cost_per_unit_inr INT,
            water_resistance INT,
            recycle_time_days INT,
            manufacturing_place VARCHAR(255)
        );
    """)

    # DDL for product_material table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_material (
            material_id INT,
            eco_alternative VARCHAR(255),
            category VARCHAR(255),
            weight_capacity_upto INT
        );
    """)
    print("Tables 'materials' and 'product_material' ensured.")

def upload_csv_to_db():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Create tables first
        create_tables(cur)

        # Clear existing data to avoid duplicates if re-running (Optional, but often desired for 'upload' scripts)
        # cur.execute("TRUNCATE TABLE product_material, materials RESTART IDENTITY;") 
        # Commented out TRUNCATE for safety, un-comment if you want to wipe data before load.
        
        csv_to_table = {
            r"D:\vscode\Infosys\data\material_data.csv": "materials",
            r"D:\vscode\Infosys\data\product_material.csv": "product_material"
        }

        for csv_path, table_name in csv_to_table.items():
            if not os.path.exists(csv_path):
                print(f"Error: File not found: {csv_path}")
                continue

            print(f"Uploading {csv_path} to table {table_name}...")
            
            with open(csv_path, "r", encoding="utf-8") as f:
                # Use COPY with HEADER to automatically handle the header row
                cur.copy_expert(
                    sql=f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)",
                    file=f
                )
        
        conn.commit()
        print("Data loaded successfully.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    upload_csv_to_db()

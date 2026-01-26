import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env_db file
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(basedir, '.env_db'))

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "ecopackai_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "123456")
    )
    print("Database connected successfully")
    conn.close()

except Exception as e:
    print("Database connection failed")
    print(e)

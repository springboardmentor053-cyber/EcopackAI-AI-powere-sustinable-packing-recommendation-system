import os

class Settings:
    DB_URL = os.getenv("DATABASE_URL")  # e.g. postgresql://user:pass@host:5432/dbname
    API_KEY = os.getenv("ECO_API_KEY", "")  # simple header key auth (optional but good)
    TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", "5"))

settings = Settings()
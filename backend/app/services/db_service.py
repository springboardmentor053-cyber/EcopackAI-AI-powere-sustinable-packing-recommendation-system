
from sqlalchemy import create_engine
import psycopg2
from flask import current_app

class DatabaseService:
    def __init__(self):
        self.engine = None

    def get_engine(self):
        """Returns the SQLAlchemy engine, creating it if necessary."""
        if self.engine is None:
            try:
                # Use current_app.config to get DB URI
                db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
                self.engine = create_engine(db_uri)
                print("✅ Database connection established.")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise e
        return self.engine

# Global instance
db_service = DatabaseService()

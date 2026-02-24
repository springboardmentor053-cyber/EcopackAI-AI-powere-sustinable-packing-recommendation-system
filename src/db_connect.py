import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="EcoPackAI_Database",
        user="postgres",
        password="Gaurav@123",
        host="localhost",
        port="5432"
    )

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="eco_packaging",
    user="postgres",
    password="123456"
)

print("Database connected successfully")
conn.close()

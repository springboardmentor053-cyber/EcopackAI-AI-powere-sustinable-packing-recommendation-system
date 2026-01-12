import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="echo_pack",
        user="postgres",
        password="123456"
    )
    print("Database connected successfully")
    conn.close()

except Exception as e:
    print("Database connection failed")
    print(e)

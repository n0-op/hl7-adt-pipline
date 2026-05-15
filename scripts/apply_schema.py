import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

with open("scripts/schema.sql", "r") as f:
    sql = f.read()

cur = conn.cursor()
cur.execute(sql)
conn.commit()
print("Schema applied successfully")

cur.close()
conn.close()
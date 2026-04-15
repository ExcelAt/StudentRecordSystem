import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(
    host="studentrecordsdb.postgres.database.azure.com",
    user="exceladmin",
    password="Abracadabra@1",
    dbname="postgres",
    sslmode="require"
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cursor = conn.cursor()

cursor.execute("CREATE DATABASE student_record_system;")

print("Database created successfully.")

cursor.close()
conn.close()
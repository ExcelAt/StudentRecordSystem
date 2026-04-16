import pandas as pd
import psycopg2
import re
import logging

# ---------------- CONFIG ----------------
DB_CONFIG = {
    "host": "studentrecordsdb.postgres.database.azure.com",
    "user": "exceladmin",
    "password": "Abracadabra@1",
    "dbname": "student_record_system",
    "sslmode": "require"
}

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="etl_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- CONNECT ----------------
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ---------------- EXTRACT ----------------
def extract(file_path):
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    elif file_path.endswith(".json"):
        return pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format")
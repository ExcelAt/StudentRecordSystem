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
    
    # ---------------- TRANSFORM ----------------
def clean_columns(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

def handle_missing(df):
    return df.fillna({
        "email": "unknown@email.com"
    })

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, str(email)))

def transform_students(df):
    df = clean_columns(df)
    df = handle_missing(df)

    df["name"] = df["name"].str.title()
    df["surname"] = df["surname"].str.title()
    df["email"] = df["email"].str.lower()

    df = df[df["email"].apply(validate_email)]
    return df

def transform_grades(df):
    df = clean_columns(df)

    # GPA calculation
    df["gpa"] = (df["assignment_grade"] + df["exam_grade"]) / 2 / 20
    return df

def transform_attendance(df):
    df = clean_columns(df)

    # Attendance analysis
    df["low_attendance"] = df["attendance_percentage"] < 75
    return df

# ---------------- LOAD ----------------
def load_data(query, data):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.executemany(query, data)
        conn.commit()
        logging.info("Data loaded successfully")

    except Exception as e:
        conn.rollback()
        logging.error(f"Load failed: {e}")

    finally:
        cursor.close()
        conn.close()

# =========================
# PHASE 4: ETL DEVELOPMENT
# =========================

import pandas as pd
import sqlite3
import logging
import re

# -------------------------
# LOGGING SETUP
# -------------------------
logging.basicConfig(
    filename="etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("ETL process started")

# -------------------------
# EXTRACT
# -------------------------
try:
    students_df = pd.read_csv("students.csv")
    courses_df = pd.read_excel("courses.xlsx")
    enrollments_df = pd.read_csv("enrollments.csv")
    grades_df = pd.read_csv("grades.csv")
    attendance_df = pd.read_json("attendance.json")

    logging.info("Data extraction completed")

# -------------------------
# TRANSFORM
# -------------------------

    # Standardize formats
    students_df["email"] = students_df["email"].str.lower().str.strip()
    students_df["dob"] = pd.to_datetime(students_df["dob"], errors="coerce")
    attendance_df["date"] = pd.to_datetime(attendance_df["date"], errors="coerce")

    # Handle missing values
    students_df.fillna("Unknown", inplace=True)

    # Remove duplicates
    students_df.drop_duplicates(subset=["email"], inplace=True)

    logging.info("Data cleaning and standardization completed")

    # Email validation
    def is_valid_email(email):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(email)))

    students_df = students_df[students_df["email"].apply(is_valid_email)]

    logging.info("Email validation completed")

    # Validate grades (0–100)
    grades_df = grades_df[(grades_df["score"] >= 0) & (grades_df["score"] <= 100)]

    # GPA calculation
    def calculate_gpa(score):
        if score >= 75:
            return 4.0
        elif score >= 65:
            return 3.0
        elif score >= 50:
            return 2.0
        else:
            return 1.0

    grades_df["GPA"] = grades_df["score"].apply(calculate_gpa)

    logging.info("GPA calculation completed")

    # Attendance validation
    attendance_df = attendance_df[attendance_df["status"].isin(["Present", "Absent"])]

    # Attendance analysis
    attendance_summary = attendance_df.groupby("student_id").apply(
        lambda x: (x["status"] == "Present").sum() / len(x) * 100
    ).reset_index(name="attendance_rate")

    logging.info("Attendance analysis completed")

# -------------------------
# LOAD (WITH ROLLBACK)
# -------------------------
    conn = sqlite3.connect("student_records.db")

    try:
        students_df.to_sql("Students", conn, if_exists="append", index=False)
        courses_df.to_sql("Courses", conn, if_exists="append", index=False)
        enrollments_df.to_sql("Enrollments", conn, if_exists="append", index=False)
        grades_df.drop(columns=["GPA"]).to_sql("Grades", conn, if_exists="append", index=False)
        attendance_df.to_sql("Attendance", conn, if_exists="append", index=False)

        conn.commit()
        logging.info("Data loaded into database successfully")

    except Exception as db_error:
        conn.rollback()
        logging.error(f"Database load failed: {db_error}")
        print("Database error:", db_error)

    finally:
        conn.close()

    print("ETL process completed successfully!")

# -------------------------
# ERROR HANDLING
# -------------------------
except Exception as e:
    logging.error(f"ETL failed: {e}")
    print("ETL Error:", e)
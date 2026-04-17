import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db_connection import get_connection

# ============================================================
# TEST UTILITIES
# ============================================================

passed = 0
failed = 0


def run_test(test_name, test_function):
    global passed, failed
    try:
        test_function()
        print(f"  PASSED  {test_name}")
        passed += 1
    except AssertionError as e:
        print(f"  FAILED  {test_name} — {str(e)}")
        failed += 1
    except Exception as e:
        print(f"  ERROR   {test_name} — {str(e)}")
        failed += 1


def print_section(title):
    print(f"\n{title}")
    print("-" * 60)


def print_summary():
    print("\n" + "=" * 60)
    print(f"  Test Summary")
    print("=" * 60)
    print(f"  Total  : {passed + failed}")
    print(f"  Passed : {passed}")
    print(f"  Failed : {failed}")
    print("=" * 60)


# ============================================================
# SECTION 1 — DATABASE CONNECTION TESTS
# ============================================================

def test_database_connection():
    conn = get_connection()
    assert conn is not None, "Connection returned None"
    conn.close()


def test_database_connection_closes_cleanly():
    conn = get_connection()
    conn.close()
    assert conn.closed != 0, "Connection did not close properly"


# ============================================================
# SECTION 2 — DATA VALIDATION TESTS
# ============================================================

def test_no_duplicate_student_emails():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, COUNT(*) as count
        FROM students
        GROUP BY email
        HAVING COUNT(*) > 1;
    """)
    duplicates = cursor.fetchall()
    cursor.close()
    conn.close()
    assert len(duplicates) == 0, (
        f"Found {len(duplicates)} duplicate email(s) in students table"
    )


def test_no_duplicate_user_emails():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, COUNT(*) as count
        FROM users
        GROUP BY email
        HAVING COUNT(*) > 1;
    """)
    duplicates = cursor.fetchall()
    cursor.close()
    conn.close()
    assert len(duplicates) == 0, (
        f"Found {len(duplicates)} duplicate email(s) in users table"
    )


def test_all_student_ids_are_unique():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students;")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT id) FROM students;")
    distinct = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert total == distinct, (
        f"Student IDs are not unique. Total: {total}, Distinct: {distinct}"
    )


def test_all_grade_values_within_valid_range():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM grades
        WHERE assignment_grade < 0 OR assignment_grade > 100
        OR exam_grade < 0 OR exam_grade > 100
        OR final_score < 0 OR final_score > 100;
    """)
    invalid_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert invalid_count == 0, (
        f"Found {invalid_count} grade record(s) outside the valid 0 to 100 range"
    )


def test_all_attendance_values_within_valid_range():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE attendance_percentage < 0 OR attendance_percentage > 100;
    """)
    invalid_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert invalid_count == 0, (
        f"Found {invalid_count} attendance record(s) outside the valid 0 to 100 range"
    )


def test_no_null_student_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM students
        WHERE name IS NULL OR surname IS NULL;
    """)
    null_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert null_count == 0, (
        f"Found {null_count} student(s) with null name or surname"
    )


def test_no_null_student_emails():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM students
        WHERE email IS NULL OR email = '';
    """)
    null_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert null_count == 0, (
        f"Found {null_count} student(s) with null or empty email"
    )


def test_all_user_roles_are_valid():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM users
        WHERE role NOT IN ('admin', 'student');
    """)
    invalid_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert invalid_count == 0, (
        f"Found {invalid_count} user(s) with invalid role"
    )


def test_all_enrollments_have_valid_student_references():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM enrollments e
        LEFT JOIN students s ON e.student_id = s.id
        WHERE s.id IS NULL;
    """)
    invalid_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert invalid_count == 0, (
        f"Found {invalid_count} enrollment(s) with invalid student reference"
    )


def test_all_enrollments_have_valid_course_references():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM enrollments e
        LEFT JOIN courses c ON e.course_id = c.id
        WHERE c.id IS NULL;
    """)
    invalid_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert invalid_count == 0, (
        f"Found {invalid_count} enrollment(s) with invalid course reference"
    )


def test_all_grades_have_valid_enrollment_references():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM grades g
        LEFT JOIN enrollments e ON g.enrollment_id = e.id
        WHERE e.id IS NULL;
    """)
    invalid_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert invalid_count == 0, (
        f"Found {invalid_count} grade record(s) with invalid enrollment reference"
    )


def test_all_attendance_have_valid_enrollment_references():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM attendance a
        LEFT JOIN enrollments e ON a.enrollment_id = e.id
        WHERE e.id IS NULL;
    """)
    invalid_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert invalid_count == 0, (
        f"Found {invalid_count} attendance record(s) with invalid enrollment reference"
    )


# ============================================================
# SECTION 3 — DATA INSERTION TESTS
# ============================================================

def test_insert_and_delete_student():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT setval('students_id_seq', (SELECT MAX(id) FROM students));
    """)

    cursor.execute("""
        INSERT INTO students (name, surname, email, date_of_birth, gender)
        VALUES ('Test', 'User', 'testuser_temp@example.com', '2000-01-01', 'Male')
        RETURNING id;
    """)
    new_id = cursor.fetchone()[0]
    conn.commit()

    assert new_id is not None, "Insert did not return a valid ID"

    cursor.execute("DELETE FROM students WHERE id = %s;", (new_id,))
    conn.commit()

    cursor.execute("SELECT id FROM students WHERE id = %s;", (new_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    assert result is None, "Test student was not deleted correctly"


def test_duplicate_email_is_rejected():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT setval('students_id_seq', (SELECT MAX(id) FROM students));
    """)

    cursor.execute("""
        INSERT INTO students (name, surname, email, date_of_birth, gender)
        VALUES ('Duplicate', 'Test', 'duplicate_temp@example.com', '2000-01-01', 'Female')
        RETURNING id;
    """)
    new_id = cursor.fetchone()[0]
    conn.commit()

    rejected = False
    try:
        cursor.execute("""
            INSERT INTO students (name, surname, email, date_of_birth, gender)
            VALUES ('Duplicate', 'Again', 'duplicate_temp@example.com', '2000-01-01', 'Female');
        """)
        conn.commit()
    except Exception:
        conn.rollback()
        rejected = True

    cursor.execute("DELETE FROM students WHERE id = %s;", (new_id,))
    conn.commit()
    cursor.close()
    conn.close()

    assert rejected, "Duplicate email was not rejected by the database"


def test_insert_grade_calculates_correctly():
    assignment = 80.0
    exam = 70.0
    expected_final = round((assignment * 0.4) + (exam * 0.6), 2)
    assert expected_final == 74.0, (
        f"Final score calculation incorrect. Expected 74.0, got {expected_final}"
    )


# ============================================================
# SECTION 4 — QUERY ACCURACY TESTS
# ============================================================

def test_student_count_is_positive():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert count > 0, "Students table returned zero records"


def test_course_count_is_positive():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert count > 0, "Courses table returned zero records"


def test_enrollment_count_is_positive():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM enrollments;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert count > 0, "Enrollments table returned zero records"


def test_average_final_score_is_within_valid_range():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(final_score) FROM grades;")
    avg = float(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    assert 0 <= avg <= 100, (
        f"Average final score {avg} is outside the valid 0 to 100 range"
    )


def test_average_attendance_is_within_valid_range():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(attendance_percentage) FROM attendance;")
    avg = float(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    assert 0 <= avg <= 100, (
        f"Average attendance {avg} is outside the valid 0 to 100 range"
    )


def test_low_attendance_query_returns_correct_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE attendance_percentage < 75;
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert count >= 0, "Low attendance query returned an invalid result"


def test_top_10_students_query_returns_ten_or_fewer():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, s.surname, AVG(g.final_score) as avg_score
        FROM grades g
        JOIN enrollments e ON g.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        GROUP BY s.id, s.name, s.surname
        ORDER BY avg_score DESC
        LIMIT 10;
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    assert len(results) <= 10, (
        f"Top 10 query returned {len(results)} results, expected 10 or fewer"
    )


def test_enrollment_count_per_course_query():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.course_name, COUNT(e.id) as total
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        GROUP BY c.course_name
        ORDER BY total DESC;
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    assert len(results) > 0, "Enrollment count per course query returned no results"


def test_admin_account_exists():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM users
        WHERE role = 'admin';
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert count >= 1, "No admin account found in the users table"


def test_student_accounts_exist():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM users
        WHERE role = 'student';
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert count > 0, "No student accounts found in the users table"


def test_every_student_has_a_user_account():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM students s
        LEFT JOIN users u ON s.id = u.student_id
        WHERE u.id IS NULL;
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert count == 0, (
        f"Found {count} student(s) without a corresponding user account"
    )


# ============================================================
# SECTION 5 — ETL PIPELINE TESTS
# ============================================================

def test_student_dataset_csv_exists():
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "students data.csv")
    assert os.path.exists(path), "students data.csv not found in student_dataset folder"


def test_courses_dataset_csv_exists():
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "courses data.csv")
    assert os.path.exists(path), "courses data.csv not found in student_dataset folder"


def test_enrollments_dataset_csv_exists():
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "enrollments data.csv")
    assert os.path.exists(path), "enrollments data.csv not found in student_dataset folder"


def test_grades_dataset_csv_exists():
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "grades data.csv")
    assert os.path.exists(path), "grades data.csv not found in student_dataset folder"


def test_attendance_dataset_csv_exists():
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "attendance data.csv")
    assert os.path.exists(path), "attendance data.csv not found in student_dataset folder"


def test_student_csv_has_required_columns():
    import pandas as pd
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "students data.csv")
    df = pd.read_csv(path)
    required_columns = {"name", "surname", "email", "date of birth", "gender"}
    actual_columns = set(df.columns.str.lower().str.strip())
    missing = required_columns - actual_columns
    assert len(missing) == 0, f"Missing columns in students CSV: {missing}"


def test_student_csv_has_no_empty_emails():
    import pandas as pd
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "students data.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower().str.strip()
    null_emails = df["email"].isnull().sum()
    assert null_emails == 0, f"Found {null_emails} null email(s) in students CSV"


def test_grades_csv_values_within_range():
    import pandas as pd
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "grades data.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower().str.strip()
    for col in ["assignment_grade", "exam_grade", "final_score"]:
        invalid = df[(df[col] < 0) | (df[col] > 100)].shape[0]
        assert invalid == 0, (
            f"Found {invalid} value(s) outside 0 to 100 range in column {col}"
        )


def test_attendance_csv_values_within_range():
    import pandas as pd
    path = os.path.join(os.path.dirname(__file__), "student_dataset", "attendance data.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower().str.strip()
    for col in ["attendance_percentage"]:
        invalid = df[(df[col] < 0) | (df[col] > 100)].shape[0]
        assert invalid == 0, (
            f"Found {invalid} value(s) outside 0 to 100 range in column {col}"
        )


# ============================================================
# MAIN TEST RUNNER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("  Student Record System — Test Suite")
    print("=" * 60)

    print_section("1. Database Connection")
    run_test("Database connects successfully", test_database_connection)
    run_test("Database connection closes cleanly", test_database_connection_closes_cleanly)

    print_section("2. Data Validation")
    run_test("No duplicate student emails", test_no_duplicate_student_emails)
    run_test("No duplicate user emails", test_no_duplicate_user_emails)
    run_test("All student IDs are unique", test_all_student_ids_are_unique)
    run_test("All grade values within 0 to 100", test_all_grade_values_within_valid_range)
    run_test("All attendance values within 0 to 100", test_all_attendance_values_within_valid_range)
    run_test("No null student names", test_no_null_student_names)
    run_test("No null student emails", test_no_null_student_emails)
    run_test("All user roles are valid", test_all_user_roles_are_valid)
    run_test("All enrollments have valid student references", test_all_enrollments_have_valid_student_references)
    run_test("All enrollments have valid course references", test_all_enrollments_have_valid_course_references)
    run_test("All grades have valid enrollment references", test_all_grades_have_valid_enrollment_references)
    run_test("All attendance records have valid enrollment references", test_all_attendance_have_valid_enrollment_references)

    print_section("3. Data Insertion")
    run_test("Insert and delete student works correctly", test_insert_and_delete_student)
    run_test("Duplicate email is rejected by database", test_duplicate_email_is_rejected)
    run_test("Grade final score calculation is correct", test_insert_grade_calculates_correctly)

    print_section("4. Query Accuracy")
    run_test("Student count is positive", test_student_count_is_positive)
    run_test("Course count is positive", test_course_count_is_positive)
    run_test("Enrollment count is positive", test_enrollment_count_is_positive)
    run_test("Average final score is within valid range", test_average_final_score_is_within_valid_range)
    run_test("Average attendance is within valid range", test_average_attendance_is_within_valid_range)
    run_test("Low attendance query returns correct results", test_low_attendance_query_returns_correct_results)
    run_test("Top 10 students query returns ten or fewer", test_top_10_students_query_returns_ten_or_fewer)
    run_test("Enrollment count per course query works", test_enrollment_count_per_course_query)
    run_test("Admin account exists", test_admin_account_exists)
    run_test("Student accounts exist", test_student_accounts_exist)
    run_test("Every student has a user account", test_every_student_has_a_user_account)

    print_section("5. ETL Pipeline")
    run_test("students data.csv exists", test_student_dataset_csv_exists)
    run_test("courses data.csv exists", test_courses_dataset_csv_exists)
    run_test("enrollments data.csv exists", test_enrollments_dataset_csv_exists)
    run_test("grades data.csv exists", test_grades_dataset_csv_exists)
    run_test("attendance data.csv exists", test_attendance_dataset_csv_exists)
    run_test("Student CSV has required columns", test_student_csv_has_required_columns)
    run_test("Student CSV has no empty emails", test_student_csv_has_no_empty_emails)
    run_test("Grades CSV values within valid range", test_grades_csv_values_within_range)
    run_test("Attendance CSV values within valid range", test_attendance_csv_values_within_range)

    print_summary()
import os

import re

from datetime import datetime

from dotenv import load_dotenv

import psycopg2
 
load_dotenv()
 
def get_connection():

    return psycopg2.connect(

        host=os.getenv("DB_HOST"),

        user=os.getenv("DB_USER"),

        password=os.getenv("DB_PASSWORD"),

        dbname=os.getenv("DB_NAME"),

        sslmode=os.getenv("DB_SSLMODE")

    )
 
NOW = lambda: datetime.now().strftime('%Y-%m-%d')
 
# ── Validation ────────────────────────────────────────────────────────────────

def valid_email(v):

    return bool(re.match(r'^[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}$', v))
 
def valid_date(v):

    try:

        datetime.strptime(v, '%Y-%m-%d')

        return True

    except:

        return False
 
def valid_score(v):

    try:

        return 0 <= float(v) <= 100

    except:

        return False
 
def valid_gender(v):

    return v.lower() in ('male', 'female', 'm', 'f')
 
def norm_gender(v):

    return 'Male' if v.lower() in ('m', 'male') else 'Female'
 
def valid_percentage(v):

    try:

        return 0 <= float(v) <= 100

    except:

        return False
 
# ── Input helpers ─────────────────────────────────────────────────────────────

def ask(prompt, validate=None, transform=None, error="Invalid input."):

    while True:

        v = input(prompt).strip()

        if validate is None or validate(v):

            return transform(v) if transform else v

        print(f"  Error: {error}")
 
def confirm(prompt):

    return input(prompt).strip().lower() == 'yes'
 
# ══════════════════════════════════════════════════════════════════════════════

# STUDENTS

# ══════════════════════════════════════════════════════════════════════════════
 
def add_student():

    print("\n── ADD STUDENT ──")

    name = ask("First Name: ", bool, error="Cannot be blank.")

    surname = ask("Surname: ", bool, error="Cannot be blank.")

    email = ask("Email: ", valid_email, error="Invalid email format.")

    dob = ask("Date of Birth (YYYY-MM-DD): ", valid_date, error="Use YYYY-MM-DD format.")

    gender = ask("Gender (Male/Female): ", valid_gender, norm_gender, "Enter Male or Female.")
 
    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            INSERT INTO students (name, surname, email, date_of_birth, gender)

            VALUES (%s, %s, %s, %s, %s)

            RETURNING id;

        """, (name, surname, email, dob, gender))

        new_id = cur.fetchone()[0]

        conn.commit()

        print(f"  Student added successfully. Student ID: {new_id}")

    except psycopg2.IntegrityError:

        print("  Error: A student with that email already exists.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def view_all_students():

    print("\n── ALL STUDENTS ──")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT id, name, surname, email, date_of_birth, gender

            FROM students

            ORDER BY id;

        """)

        rows = cur.fetchall()

        if not rows:

            print("  No students found.")

            return

        print(f"\n  {'ID':<6}{'Name':<20}{'Surname':<20}{'Email':<30}{'DOB':<14}{'Gender'}")

        print("  " + "-" * 95)

        for row in rows:

            print(f"  {row[0]:<6}{row[1]:<20}{row[2]:<20}{row[3]:<30}{str(row[4]):<14}{row[5]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def view_student():

    print("\n── VIEW STUDENT ──")

    sid = ask("Student ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT id, name, surname, email, date_of_birth, gender

            FROM students WHERE id = %s;

        """, (int(sid),))

        row = cur.fetchone()

        if not row:

            print("  Student not found.")

            return

        print(f"\n  ID: {row[0]}")

        print(f"  Name: {row[1]} {row[2]}")

        print(f"  Email: {row[3]}")

        print(f"  Date of Birth: {row[4]}")

        print(f"  Gender: {row[5]}")
 
        cur.execute("""

            SELECT c.course_name, e.id

            FROM enrollments e

            JOIN courses c ON e.course_id = c.id

            WHERE e.student_id = %s;

        """, (int(sid),))

        enrollments = cur.fetchall()

        if enrollments:

            print(f"\n  Enrolled Courses:")

            for en in enrollments:

                print(f"    - {en[0]} (Enrollment ID: {en[1]})")

        else:

            print("\n  Not enrolled in any courses.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def update_student():

    print("\n── UPDATE STUDENT ──")

    sid = ask("Student ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("SELECT id, name, surname, email, date_of_birth, gender FROM students WHERE id = %s;", (int(sid),))

        row = cur.fetchone()

        if not row:

            print("  Student not found.")

            return
 
        print(f"\n  1. Name:          {row[1]}")

        print(f"  2. Surname:       {row[2]}")

        print(f"  3. Email:         {row[3]}")

        print(f"  4. Date of Birth: {row[4]}")

        print(f"  5. Gender:        {row[5]}")

        print(f"  0. Cancel")
 
        choice = input("\n  Update which field? (0-5): ").strip()
 
        field_map = {

            '1': ('name', None, None),

            '2': ('surname', None, None),

            '3': ('email', valid_email, "Invalid email format."),

            '4': ('date_of_birth', valid_date, "Use YYYY-MM-DD format."),

            '5': ('gender', valid_gender, "Enter Male or Female."),

        }
 
        if choice == '0':

            return

        if choice not in field_map:

            print("  Invalid choice.")

            return
 
        field, validator, error = field_map[choice]

        transform = norm_gender if field == 'gender' else None

        new_value = ask(f"  New value: ", validator, transform, error)
 
        cur.execute(f"UPDATE students SET {field} = %s WHERE id = %s;", (new_value, int(sid)))

        conn.commit()

        print("  Student updated successfully.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def delete_student():

    print("\n── DELETE STUDENT ──")

    sid = ask("Student ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("SELECT name, surname FROM students WHERE id = %s;", (int(sid),))

        row = cur.fetchone()

        if not row:

            print("  Student not found.")

            return

        name = f"{row[0]} {row[1]}"

        if not confirm(f"  Delete '{name}'? This will remove all their enrollments, grades and attendance. (yes/no): "):

            print("  Cancelled.")

            return

        cur.execute("DELETE FROM students WHERE id = %s;", (int(sid),))

        conn.commit()

        print(f"  '{name}' deleted successfully.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
# ══════════════════════════════════════════════════════════════════════════════

# COURSES

# ══════════════════════════════════════════════════════════════════════════════
 
def view_all_courses():

    print("\n── ALL COURSES ──")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("SELECT id, course_name, major, duration_months FROM courses ORDER BY id;")

        rows = cur.fetchall()

        if not rows:

            print("  No courses found.")

            return

        print(f"\n  {'ID':<6}{'Course Name':<35}{'Major':<25}{'Duration (months)'}")

        print("  " + "-" * 80)

        for row in rows:

            print(f"  {row[0]:<6}{row[1]:<35}{row[2]:<25}{row[3]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
# ══════════════════════════════════════════════════════════════════════════════

# ENROLLMENTS

# ══════════════════════════════════════════════════════════════════════════════
 
def enroll_student():

    print("\n── ENROLL STUDENT ──")

    sid = ask("Student ID: ", str.isdigit, error="Must be a number.")

    view_all_courses()

    cid = ask("Course ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()
 
        cur.execute("SELECT name, surname FROM students WHERE id = %s;", (int(sid),))

        student = cur.fetchone()

        if not student:

            print("  Student not found.")

            return
 
        cur.execute("SELECT course_name FROM courses WHERE id = %s;", (int(cid),))

        course = cur.fetchone()

        if not course:

            print("  Course not found.")

            return
 
        cur.execute("""

            SELECT id FROM enrollments

            WHERE student_id = %s AND course_id = %s;

        """, (int(sid), int(cid)))

        if cur.fetchone():

            print("  Student is already enrolled in this course.")

            return
 
        cur.execute("""

            INSERT INTO enrollments (student_id, course_id)

            VALUES (%s, %s) RETURNING id;

        """, (int(sid), int(cid)))

        enrollment_id = cur.fetchone()[0]

        conn.commit()

        print(f"  {student[0]} {student[1]} enrolled in {course[0]}.")

        print(f"  Enrollment ID: {enrollment_id}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def view_enrollments():

    print("\n── ALL ENROLLMENTS ──")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT e.id, s.id, s.name, s.surname, c.id, c.course_name

            FROM enrollments e

            JOIN students s ON e.student_id = s.id

            JOIN courses c ON e.course_id = c.id

            ORDER BY e.id;

        """)

        rows = cur.fetchall()

        if not rows:

            print("  No enrollments found.")

            return

        print(f"\n  {'Enroll ID':<12}{'Std ID':<8}{'Student':<25}{'Crs ID':<8}{'Course'}")

        print("  " + "-" * 80)

        for row in rows:

            print(f"  {row[0]:<12}{row[1]:<8}{(row[2]+' '+row[3])[:25]:<25}{row[4]:<8}{row[5]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def unenroll_student():

    print("\n── UNENROLL STUDENT ──")

    eid = ask("Enrollment ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT s.name, s.surname, c.course_name

            FROM enrollments e

            JOIN students s ON e.student_id = s.id

            JOIN courses c ON e.course_id = c.id

            WHERE e.id = %s;

        """, (int(eid),))

        row = cur.fetchone()

        if not row:

            print("  Enrollment not found.")

            return

        if not confirm(f"  Unenroll {row[0]} {row[1]} from {row[2]}? This removes their grades and attendance too. (yes/no): "):

            print("  Cancelled.")

            return

        cur.execute("DELETE FROM enrollments WHERE id = %s;", (int(eid),))

        conn.commit()

        print("  Unenrolled successfully.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
# ══════════════════════════════════════════════════════════════════════════════

# GRADES

# ══════════════════════════════════════════════════════════════════════════════
 
def record_grade():

    print("\n── RECORD GRADE ──")

    eid = ask("Enrollment ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT s.name, s.surname, c.course_name

            FROM enrollments e

            JOIN students s ON e.student_id = s.id

            JOIN courses c ON e.course_id = c.id

            WHERE e.id = %s;

        """, (int(eid),))

        row = cur.fetchone()

        if not row:

            print("  Enrollment not found.")

            return

        print(f"  Student: {row[0]} {row[1]}  |  Course: {row[2]}")
 
        assignment = ask("  Assignment Grade (0-100): ", valid_score, error="Enter a number between 0 and 100.")

        exam = ask("  Exam Grade (0-100): ", valid_score, error="Enter a number between 0 and 100.")

        final = ask("  Final Score (0-100): ", valid_score, error="Enter a number between 0 and 100.")
 
        cur.execute("""

            INSERT INTO grades (enrollment_id, assignment_grade, exam_grade, final_score)

            VALUES (%s, %s, %s, %s)

            ON CONFLICT (enrollment_id) DO UPDATE

            SET assignment_grade = EXCLUDED.assignment_grade,

                exam_grade = EXCLUDED.exam_grade,

                final_score = EXCLUDED.final_score;

        """, (int(eid), float(assignment), float(exam), float(final)))

        conn.commit()

        print("  Grade recorded successfully.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def view_grades():

    print("\n── ALL GRADES ──")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT s.id, s.name, s.surname, c.course_name,

                   g.assignment_grade, g.exam_grade, g.final_score

            FROM grades g

            JOIN enrollments e ON g.enrollment_id = e.id

            JOIN students s ON e.student_id = s.id

            JOIN courses c ON e.course_id = c.id

            ORDER BY s.id;

        """)

        rows = cur.fetchall()

        if not rows:

            print("  No grades found.")

            return

        print(f"\n  {'Std ID':<8}{'Name':<25}{'Course':<30}{'Assign':<10}{'Exam':<10}{'Final'}")

        print("  " + "-" * 90)

        for row in rows:

            print(f"  {row[0]:<8}{(row[1]+' '+row[2])[:25]:<25}{row[3][:30]:<30}{str(row[4]):<10}{str(row[5]):<10}{row[6]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def view_student_grades():

    print("\n── STUDENT GRADES ──")

    sid = ask("Student ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT c.course_name, g.assignment_grade, g.exam_grade, g.final_score

            FROM grades g

            JOIN enrollments e ON g.enrollment_id = e.id

            JOIN courses c ON e.course_id = c.id

            WHERE e.student_id = %s

            ORDER BY c.course_name;

        """, (int(sid),))

        rows = cur.fetchall()

        if not rows:

            print("  No grades found for this student.")

            return

        print(f"\n  {'Course':<35}{'Assignment':<14}{'Exam':<10}{'Final'}")

        print("  " + "-" * 65)

        for row in rows:

            print(f"  {row[0][:35]:<35}{str(row[1]):<14}{str(row[2]):<10}{row[3]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
# ══════════════════════════════════════════════════════════════════════════════

# ATTENDANCE

# ══════════════════════════════════════════════════════════════════════════════
 
def mark_attendance():

    print("\n── MARK ATTENDANCE ──")

    eid = ask("Enrollment ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT s.name, s.surname, c.course_name

            FROM enrollments e

            JOIN students s ON e.student_id = s.id

            JOIN courses c ON e.course_id = c.id

            WHERE e.id = %s;

        """, (int(eid),))

        row = cur.fetchone()

        if not row:

            print("  Enrollment not found.")

            return

        print(f"  Student: {row[0]} {row[1]}  |  Course: {row[2]}")
 
        percentage = ask("  Attendance Percentage (0-100): ", valid_percentage,

                        error="Enter a number between 0 and 100.")
 
        cur.execute("""

            INSERT INTO attendance (enrollment_id, attendance_percentage)

            VALUES (%s, %s)

            ON CONFLICT (enrollment_id) DO UPDATE

            SET attendance_percentage = EXCLUDED.attendance_percentage;

        """, (int(eid), float(percentage)))

        conn.commit()

        print("  Attendance recorded successfully.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def view_attendance():

    print("\n── ALL ATTENDANCE ──")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT s.id, s.name, s.surname, c.course_name, a.attendance_percentage

            FROM attendance a

            JOIN enrollments e ON a.enrollment_id = e.id

            JOIN students s ON e.student_id = s.id

            JOIN courses c ON e.course_id = c.id

            ORDER BY s.id;

        """)

        rows = cur.fetchall()

        if not rows:

            print("  No attendance records found.")

            return

        print(f"\n  {'Std ID':<8}{'Name':<25}{'Course':<35}{'Attendance %'}")

        print("  " + "-" * 80)

        for row in rows:

            print(f"  {row[0]:<8}{(row[1]+' '+row[2])[:25]:<25}{row[3][:35]:<35}{row[4]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def view_student_attendance():

    print("\n── STUDENT ATTENDANCE ──")

    sid = ask("Student ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT c.course_name, a.attendance_percentage

            FROM attendance a

            JOIN enrollments e ON a.enrollment_id = e.id

            JOIN courses c ON e.course_id = c.id

            WHERE e.student_id = %s

            ORDER BY c.course_name;

        """, (int(sid),))

        rows = cur.fetchall()

        if not rows:

            print("  No attendance records found for this student.")

            return

        print(f"\n  {'Course':<40}{'Attendance %'}")

        print("  " + "-" * 55)

        for row in rows:

            print(f"  {row[0][:40]:<40}{row[1]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
# ══════════════════════════════════════════════════════════════════════════════

# REPORTS

# ══════════════════════════════════════════════════════════════════════════════
 
def generate_student_report():

    print("\n── STUDENT REPORT ──")

    sid = ask("Student ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT id, name, surname, email, date_of_birth, gender

            FROM students WHERE id = %s;

        """, (int(sid),))

        student = cur.fetchone()

        if not student:

            print("  Student not found.")

            return
 
        print(f"\n  Student Report")

        print(f"  Generated: {NOW()}")

        print(f"\n  ID:            {student[0]}")

        print(f"  Name:          {student[1]} {student[2]}")

        print(f"  Email:         {student[3]}")

        print(f"  Date of Birth: {student[4]}")

        print(f"  Gender:        {student[5]}")
 
        cur.execute("""

            SELECT c.course_name, g.assignment_grade, g.exam_grade,

                   g.final_score, a.attendance_percentage

            FROM enrollments e

            JOIN courses c ON e.course_id = c.id

            LEFT JOIN grades g ON g.enrollment_id = e.id

            LEFT JOIN attendance a ON a.enrollment_id = e.id

            WHERE e.student_id = %s;

        """, (int(sid),))

        rows = cur.fetchall()

        if rows:

            print(f"\n  {'Course':<35}{'Assign':<10}{'Exam':<10}{'Final':<10}{'Attend%'}")

            print("  " + "-" * 75)

            for row in rows:

                print(f"  {row[0][:35]:<35}{str(row[1]):<10}{str(row[2]):<10}{str(row[3]):<10}{row[4]}")

        else:

            print("\n  Not enrolled in any courses.")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def generate_course_report():

    print("\n── COURSE REPORT ──")

    view_all_courses()

    cid = ask("Course ID: ", str.isdigit, error="Must be a number.")

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

            SELECT id, course_name, major, duration_months

            FROM courses WHERE id = %s;

        """, (int(cid),))

        course = cur.fetchone()

        if not course:

            print("  Course not found.")

            return
 
        print(f"\n  Course Report")

        print(f"  Generated: {NOW()}")

        print(f"\n  ID:       {course[0]}")

        print(f"  Course:   {course[1]}")

        print(f"  Major:    {course[2]}")

        print(f"  Duration: {course[3]} months")
 
        cur.execute("""

            SELECT s.id, s.name, s.surname, g.assignment_grade,

                   g.exam_grade, g.final_score, a.attendance_percentage

            FROM enrollments e

            JOIN students s ON e.student_id = s.id

            LEFT JOIN grades g ON g.enrollment_id = e.id

            LEFT JOIN attendance a ON a.enrollment_id = e.id

            WHERE e.course_id = %s

            ORDER BY s.surname;

        """, (int(cid),))

        rows = cur.fetchall()

        print(f"\n  Enrolled Students: {len(rows)}")

        if rows:

            print(f"\n  {'ID':<6}{'Name':<25}{'Assign':<10}{'Exam':<10}{'Final':<10}{'Attend%'}")

            print("  " + "-" * 75)

            for row in rows:

                print(f"  {row[0]:<6}{(row[1]+' '+row[2])[:25]:<25}{str(row[3]):<10}{str(row[4]):<10}{str(row[5]):<10}{row[6]}")

    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
def generate_summary_report():

    print("\n── SUMMARY REPORT ──")

    try:

        conn = get_connection()

        cur = conn.cursor()
 
        cur.execute("SELECT COUNT(*) FROM students;")

        total_students = cur.fetchone()[0]
 
        cur.execute("SELECT COUNT(*) FROM courses;")

        total_courses = cur.fetchone()[0]
 
        cur.execute("SELECT COUNT(*) FROM enrollments;")

        total_enrollments = cur.fetchone()[0]
 
        cur.execute("SELECT COUNT(*) FROM grades;")

        total_grades = cur.fetchone()[0]
 
        cur.execute("SELECT COUNT(*) FROM attendance;")

        total_attendance = cur.fetchone()[0]
 
        cur.execute("SELECT ROUND(AVG(final_score), 2) FROM grades;")

        avg_final = cur.fetchone()[0]
 
        cur.execute("SELECT ROUND(AVG(attendance_percentage), 2) FROM attendance;")

        avg_attendance = cur.fetchone()[0]
 
        cur.execute("""

            SELECT

                CASE

                    WHEN final_score >= 90 THEN 'A'

                    WHEN final_score >= 80 THEN 'B'

                    WHEN final_score >= 70 THEN 'C'

                    WHEN final_score >= 60 THEN 'D'

                    ELSE 'F'

                END AS grade,

                COUNT(*) AS count

            FROM grades

            GROUP BY grade

            ORDER BY grade;

        """)

        grade_dist = cur.fetchall()
 
        print(f"\n  Summary Report")

        print(f"  Generated: {NOW()}")

        print(f"\n  Total Students:    {total_students}")

        print(f"  Total Courses:     {total_courses}")

        print(f"  Total Enrollments: {total_enrollments}")

        print(f"  Total Grades:      {total_grades}")

        print(f"  Total Attendance:  {total_attendance}")

        print(f"\n  Average Final Score:      {avg_final}%")

        print(f"  Average Attendance Rate:  {avg_attendance}%")
 
        if grade_dist:

            print(f"\n  Grade Distribution:")

            for row in grade_dist:

                print(f"    {row[0]}: {row[1]} students")
 
    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
# ══════════════════════════════════════════════════════════════════════════════

# EXPORT

# ══════════════════════════════════════════════════════════════════════════════
 
def export_dir():

    d = os.path.join("exports")

    os.makedirs(d, exist_ok=True)

    return d
 
def export_to_csv():

    print("\n── EXPORT TO CSV ──")

    print("  1. Students")

    print("  2. Courses")

    print("  3. Enrollments")

    print("  4. Grades")

    print("  5. Attendance")

    print("  0. Cancel")
 
    choice = input("\n  Choice: ").strip()

    if choice == '0':

        return
 
    import csv

    from datetime import datetime

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')

    d = export_dir()
 
    try:

        conn = get_connection()

        cur = conn.cursor()
 
        if choice == '1':

            cur.execute("SELECT id, name, surname, email, date_of_birth, gender FROM students ORDER BY id;")

            rows = cur.fetchall()

            fp = os.path.join(d, f"students_{ts}.csv")

            with open(fp, 'w', newline='') as f:

                w = csv.writer(f)

                w.writerow(['id', 'name', 'surname', 'email', 'date_of_birth', 'gender'])

                w.writerows(rows)

            print(f"  Exported {len(rows)} students to {fp}")
 
        elif choice == '2':

            cur.execute("SELECT id, course_name, major, duration_months FROM courses ORDER BY id;")

            rows = cur.fetchall()

            fp = os.path.join(d, f"courses_{ts}.csv")

            with open(fp, 'w', newline='') as f:

                w = csv.writer(f)

                w.writerow(['id', 'course_name', 'major', 'duration_months'])

                w.writerows(rows)

            print(f"  Exported {len(rows)} courses to {fp}")
 
        elif choice == '3':

            cur.execute("SELECT id, student_id, course_id FROM enrollments ORDER BY id;")

            rows = cur.fetchall()

            fp = os.path.join(d, f"enrollments_{ts}.csv")

            with open(fp, 'w', newline='') as f:

                w = csv.writer(f)

                w.writerow(['id', 'student_id', 'course_id'])

                w.writerows(rows)

            print(f"  Exported {len(rows)} enrollments to {fp}")
 
        elif choice == '4':

            cur.execute("""

                SELECT id, enrollment_id, assignment_grade, exam_grade, final_score

                FROM grades ORDER BY id;

            """)

            rows = cur.fetchall()

            fp = os.path.join(d, f"grades_{ts}.csv")

            with open(fp, 'w', newline='') as f:

                w = csv.writer(f)

                w.writerow(['id', 'enrollment_id', 'assignment_grade', 'exam_grade', 'final_score'])

                w.writerows(rows)

            print(f"  Exported {len(rows)} grade records to {fp}")
 
        elif choice == '5':

            cur.execute("""

                SELECT id, enrollment_id, attendance_percentage

                FROM attendance ORDER BY id;

            """)

            rows = cur.fetchall()

            fp = os.path.join(d, f"attendance_{ts}.csv")

            with open(fp, 'w', newline='') as f:

                w = csv.writer(f)

                w.writerow(['id', 'enrollment_id', 'attendance_percentage'])

                w.writerows(rows)

            print(f"  Exported {len(rows)} attendance records to {fp}")
 
        else:

            print("  Invalid choice.")
 
    except Exception as e:

        print(f"  Error: {e}")

    finally:

        cur.close()

        conn.close()
 
 
# ══════════════════════════════════════════════════════════════════════════════

# MENU

# ══════════════════════════════════════════════════════════════════════════════
 
MENU = """

  ============================================

    STUDENT RECORD SYSTEM

  ============================================

  STUDENTS                ENROLLMENTS

    1.  Add Student          7.  Enroll Student

    2.  View All Students    8.  View Enrollments

    3.  View Student         9.  Unenroll Student

    4.  Update Student

    5.  Delete Student      EXPORT

    6.  View Courses         19. Export to CSV
 
  GRADES                  REPORTS

    10. Record Grade         16. Student Report

    11. View All Grades      17. Course Report

    12. Student Grades       18. Summary Report
 
  ATTENDANCE

    13. Mark Attendance

    14. View All Attendance

    15. Student Attendance
 
    0.  Exit

  ============================================"""
 
 
def run_cli():

    print("\n  Connecting to database...")

    try:

        conn = get_connection()

        conn.close()

        print("  Connected successfully.")

    except Exception as e:

        print(f"  Failed to connect to database: {e}")

        return
 
    actions = {

        '1':  add_student,

        '2':  view_all_students,

        '3':  view_student,

        '4':  update_student,

        '5':  delete_student,

        '6':  view_all_courses,

        '7':  enroll_student,

        '8':  view_enrollments,

        '9':  unenroll_student,

        '10': record_grade,

        '11': view_grades,

        '12': view_student_grades,

        '13': mark_attendance,

        '14': view_attendance,

        '15': view_student_attendance,

        '16': generate_student_report,

        '17': generate_course_report,

        '18': generate_summary_report,

        '19': export_to_csv,

    }
 
    while True:

        print(MENU)

        choice = input("  Choice (0-19): ").strip()

        if choice == '0':

            print("\n  Goodbye.\n")

            break

        action = actions.get(choice)

        if action:

            action()

        else:

            print("  Invalid choice.")

        input("\n  Press Enter to continue...")
 
 
if __name__ == "__main__":

    run_cli()
 
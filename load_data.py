import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="studentrecordsdb.postgres.database.azure.com",
    user="exceladmin",
    password="Abracadabra@1",
    dbname="student_record_system",
    sslmode="require"
)

cursor = conn.cursor()

# Load students
students = pd.read_csv("student_dataset/students data.csv")
for _, row in students.iterrows():
    cursor.execute("""
        INSERT INTO students (id, name, surname, email, date_of_birth, gender)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (int(row['id']), str(row['name']), str(row['surname']),
          str(row['email']), str(row['date of birth']), str(row['gender'])))

print("Students loaded.")

# Load courses
courses = pd.read_csv("student_dataset/courses data.csv")
for _, row in courses.iterrows():
    cursor.execute("""
        INSERT INTO courses (id, course_name, major, duration_months)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (int(row['id']), str(row['course_name']),
          str(row['major']), int(row['duration_months'])))

print("Courses loaded.")

# Load enrollments
enrollments = pd.read_csv("student_dataset/enrollments data.csv")
for _, row in enrollments.iterrows():
    cursor.execute("""
        INSERT INTO enrollments (id, student_id, course_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (int(row['id']), int(row['student_id']), int(row['course_id'])))

print("Enrollments loaded.")

# Load grades
grades = pd.read_csv("student_dataset/grades data.csv")
for _, row in grades.iterrows():
    cursor.execute("""
        INSERT INTO grades (id, enrollment_id, assignment_grade,
                           exam_grade, final_score)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (int(row['id']), int(row['enrollment_id']),
          float(row['assignment_grade']), float(row['exam_grade']),
          float(row['final_score'])))

print("Grades loaded.")

# Load attendance
attendance = pd.read_csv("student_dataset/attendance data.csv")
for _, row in attendance.iterrows():
    cursor.execute("""
        INSERT INTO attendance (id, enrollment_id, attendance_percentage)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (int(row['id']), int(row['enrollment_id']),
          float(row['attendance_percentage'])))

print("Attendance loaded.")

conn.commit()
print("All data loaded successfully.")

cursor.close()
conn.close()
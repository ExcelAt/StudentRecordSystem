from faker import Faker
import random
import pandas as pd 
from datetime import datetime

fakeData = Faker()

# Generate 497 fake student records with unique student IDs, names, ages, and  dates
students = []

for i in range(1, 498):
    students.append({
    "student_id":  i, 
    "name": fakeData.name(),
    "surname": fakeData.last_name(),
    "email": fakeData.email(),
    "date_of_birth": fakeData.date_of_birth(tzinfo=None, minimum_age=18, maximum_age=45).strftime("%Y-%m-%d"), 
    "gender": random.choice(['Male', 'Female'])

    })

students_df = pd.DataFrame(students)

# creaton of courses 
# CREATE FULL COURSES DATASET (30 COURSES)
courses_list = [
    ("Data Analytics", "Data Science"),
    ("Machine Learning", "Data Science"),
    ("Database Systems", "Information Systems"),
    ("Cloud Computing", "Computer Science"),
    ("Cybersecurity", "Information Systems"),
    ("Business Intelligence", "Business Analytics"),
    ("Python Programming", "Computer Science"),
    ("Web Development", "Computer Science"),
    ("Data Visualization", "Data Science"),
    ("AI Fundamentals", "Data Science")
]

courses = []

for i, (course_name, major) in enumerate(courses_list, start=1):
    courses.append({
        "course_id": i,
        "course_name": course_name,
        "major": major,  # keeping your schema spelling
        "duration_months": random.randint(1, 24)
    })

df_courses = pd.DataFrame(courses)

# -----------------------------
# 3. ENROLLMENTS TABLE
# -----------------------------
num_enrollments = 400
enrollments = []

for i in range(1, num_enrollments + 1):
    enrollments.append({
        "enrollment_id": i,
        "student_id": random.choice(students_df["student_id"].tolist()),
        "course_id": random.choice(df_courses["course_id"].tolist())
    })

df_enrollments = pd.DataFrame(enrollments)

# -----------------------------
# 4. GRADES TABLE
# -----------------------------
grades = []

for i, enrollment in df_enrollments.iterrows():
    assignment = round(random.uniform(40, 100), 2)
    exam = round(random.uniform(40, 100), 2)
    final = round((assignment * 0.4 + exam * 0.6), 2)

    grades.append({
        "grade_id": i + 1,
        "enrollment_id": enrollment["enrollment_id"],
        "assignment_grade": assignment,
        "exam_grade": exam,
        "final_grade": final
    })

df_grades = pd.DataFrame(grades)

# -----------------------------
# 5. ATTENDANCE TABLE
# -----------------------------
attendance = []

for i, enrollment in df_enrollments.iterrows():
    attendance.append({
        "attendance_id": i + 1,
        "enrollment_id": enrollment["enrollment_id"],
        "attendance_percentage": round(random.uniform(50, 100), 2)
    })

df_attendance = pd.DataFrame(attendance)

# -----------------------------
# 6. SAVE ALL FILES
# -----------------------------
students_df.to_csv("students.csv", index=False)
df_courses.to_csv("courses.csv", index=False)
df_enrollments.to_csv("enrollments.csv", index=False)
df_grades.to_csv("grades.csv", index=False)
df_attendance.to_csv("attendance.csv", index=False)

print("✅ All datasets generated successfully!")




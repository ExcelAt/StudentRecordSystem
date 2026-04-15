# importing important libaries
from faker import Faker 
import pandas as pan
import sqlite3
import random

dataGen = Faker()

# connect = sqlite3.connect()
#------------------------------------------------------------
# 1 create the students table with 456 records using faker
#------------------------------------------------------------
students = []
for i in range(1, 457):
    student = {
        'id': i,
        'name': dataGen.name(),
        'surname': dataGen.last_name(),
        'email': dataGen.email(), 
        'date of birth': dataGen.date_of_birth(
            minimum_age=18, 
            maximum_age=40).strftime('%Y-%m-%d'),
        'gender': random.choice(['Male', 'Female'])
    }

    students.append(student) 

studentBase = pan.DataFrame(students)

#------------------------------------------------------------
# 2 creating the courses list with 25 records
#------------------------------------------------------------
coursesRecords = [
    #IT (6)
    ("Cloud Computing", "Computer Science"),
    ("Cybersecurity", "Information Systems"),
    ("Python Programming", "Computer Science"),
    ("Web Development", "Computer Science"),
    ("Database Systems", "Information Systems"),
    ("Networking Fundamentals", "Computer Science"),

    # Business (6)
    ("Entrepreneurship", "Business"),
    ("Marketing Management", "Business"),
    ("Human Resource Management", "Business"),
    ("Operations Management", "Business"),
    ("Business Communication", "Business"),

    # Law (4)
    ("Business Law", "Law"),
    ("Contract Law", "Law"),
    ("Corporate Law", "Law"),
    ("Constitutional Law", "Law"),
    ("International Trade Law", "Law"),

    # Money and Finance (5)
    ("Financial Accounting", "Accounting"),
    ("Management Accounting", "Accounting"),
    ("Taxation", "Accounting"),
    ("Auditing", "Accounting"),
    ("Corporate Finance", "Finance"),

    # Data Science / Analytics (4)
    ("Data Analytics", "Data Science"),
    ("Business Intelligence", "Business Analytics"),
    ("Statistics", "Data Science"),
    ("Research Methods", "Information Systems"),
]
    
# creaing an empty list to store the courses data
courses = []

for i, (course_id, major) in enumerate(coursesRecords, start=1):
    course = {
        'id': i,
        'course_name': course_id,
        'major': major, 
        'duration_months': random.randint(1, 18)
    }
    courses.append(course)

coursesBase = pan.DataFrame(courses)

#------------------------------------------------------------
# 3 creating the enrollments table with 1000 records
#------------------------------------------------------------

# every student needs to be enrolled in at least 1 course at most 5
enrollments = []

student_ids = studentBase['id'].tolist()
course_ids = coursesBase['id'].tolist()

enrollment_id = 1
pairs = set()  # To track unique student-course pairs

# Enroll each student in at least 1 course
for stID in student_ids:
    cID = random.choice(course_ids)
    enrollments.append({
        'id': enrollment_id,
        'student_id': stID,
        'course_id': cID
    })
    pairs.add((stID, cID))
    enrollment_id += 1


    
min_records = 2500 
while len(enrollments) < min_records: 
    stID = random.choice(student_ids)
    cID = random.choice(course_ids)
    
    if (stID, cID) not in pairs:
        enrollments.append({
            'id': enrollment_id,
            'student_id': stID,
            'course_id': cID
        })
        pairs.add((stID, cID))
        enrollment_id += 1

enrollBase = pan.DataFrame(enrollments)

#------------------------------------------------------------
# 4 creating the grades table
#------------------------------------------------------------

# every entrollment gets a grade between 0 and 100
# assignment (40) and exam (60)
grades = []

for i, enrollment in enrollBase.iterrows():
    assignment_grade = round(random.uniform(0, 100), 2)
    exam_grade = round(random.uniform(0, 100), 2)

    final_score = round((assignment_grade * 0.4) + (exam_grade * 0.6), 2)
    
    
    grades.append({
        'id': i + 1,
        'enrollment_id': enrollment['id'],
        'assignment_grade': assignment_grade,
        'exam_grade': exam_grade, 
        'final_score': final_score
    })

gradesBase = pan.DataFrame(grades)


#------------------------------------------------------------
# 5 creating the attendance table, data
#------------------------------------------------------------

attendance = [] 

for i, enrollment in enrollBase.iterrows():
    attendance.append({
        'id': i + 1,
        'enrollment_id': enrollment['id'],
        'attendance_percentage': round(random.uniform(0, 100), 2)
    })

attendanceBase = pan.DataFrame(attendance)

#------------------------------------------------------------
# 6 converting the dataframes to csv files
#------------------------------------------------------------
#saving each dataframe as a csv file without the index column


studentBase.to_csv('students data.csv', index=False)
coursesBase.to_csv('courses data.csv', index=False)
enrollBase.to_csv('enrollments data.csv', index=False)
gradesBase.to_csv('grades data.csv', index=False)
attendanceBase.to_csv('attendance data.csv', index=False)

print(f"✅ Students:    {len(studentBase)}")
print(f"✅ Courses:     {len(coursesBase)}")
print(f"✅ Enrollments: {len(enrollBase)}")
print(f"✅ Grades:      {len(gradesBase)}")
print(f"✅ Attendance:  {len(attendanceBase)}")
print("\n🎉 All datasets generated and saved as CSV files!")
import psycopg2

conn = psycopg2.connect(
    host="studentrecordsdb.postgres.database.azure.com",
    user="exceladmin",
    password="Abracadabra@1",
    dbname="student_record_system",
    sslmode="require"
)

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        surname VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        date_of_birth DATE,
        gender VARCHAR(10)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id SERIAL PRIMARY KEY,
        course_name VARCHAR(150) NOT NULL,
        major VARCHAR(100),
        duration_months INT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id SERIAL PRIMARY KEY,
        student_id INT NOT NULL,
        course_id INT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS grades (
        id SERIAL PRIMARY KEY,
        enrollment_id INT NOT NULL,
        assignment_grade DECIMAL(5,2),
        exam_grade DECIMAL(5,2),
        final_score DECIMAL(5,2),
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
        enrollment_id INT NOT NULL,
        attendance_percentage DECIMAL(5,2),
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
    );
""")

conn.commit()
print("All tables created successfully.")

cursor.close()
conn.close()
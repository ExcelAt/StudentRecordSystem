



-- SECTION 0: CREATE DATABASE


CREATE DATABASE IF NOT EXISTS student_record_system;

USE student_record_system;



-- SECTION 1: CREATE TABLES


CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    major VARCHAR(100),
    duration_months INT
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT NOT NULL,
    assignment_grade DECIMAL(5,2),
    exam_grade DECIMAL(5,2),
    final_score DECIMAL(5,2),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT NOT NULL,
    attendance_percentage DECIMAL(5,2),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
);



-- SECTION 2: QUERIES


-- Query 1: List all students enrolled in a specific course
-- Replace the course_id value to filter by a different course

SELECT
    s.id AS student_id,
    s.name,
    s.surname,
    s.email,
    c.course_name
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id
WHERE c.id = 1
ORDER BY s.surname, s.name;


-- Query 2: Calculate average grades per course

SELECT
    c.course_name,
    ROUND(AVG(g.assignment_grade), 2) AS avg_assignment_grade,
    ROUND(AVG(g.exam_grade), 2) AS avg_exam_grade,
    ROUND(AVG(g.final_score), 2) AS avg_final_score
FROM courses c
JOIN enrollments e ON c.id = e.course_id
JOIN grades g ON e.id = g.enrollment_id
GROUP BY c.id, c.course_name
ORDER BY avg_final_score DESC;


-- Query 3: Identify students with low attendance (below 75%)

SELECT
    s.id AS student_id,
    s.name,
    s.surname,
    c.course_name,
    a.attendance_percentage
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id
JOIN attendance a ON e.id = a.enrollment_id
WHERE a.attendance_percentage < 75
ORDER BY a.attendance_percentage ASC;


-- Query 4: Top 10 students by GPA
-- GPA is derived from final_score using the standard 4.0 scale

SELECT
    s.id AS student_id,
    s.name,
    s.surname,
    ROUND(AVG(g.final_score), 2) AS avg_final_score,
    ROUND(AVG(
        CASE
            WHEN g.final_score >= 90 THEN 4.0
            WHEN g.final_score >= 80 THEN 3.0
            WHEN g.final_score >= 70 THEN 2.0
            WHEN g.final_score >= 60 THEN 1.0
            ELSE 0.0
        END
    ), 2) AS gpa
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN grades g ON e.id = g.enrollment_id
GROUP BY s.id, s.name, s.surname
ORDER BY gpa DESC
LIMIT 10;


-- Query 5: Course statistics

SELECT
    c.id AS course_id,
    c.course_name,
    c.major,
    c.duration_months,
    COUNT(DISTINCT e.student_id) AS total_students,
    ROUND(AVG(g.final_score), 2) AS avg_final_score,
    ROUND(MAX(g.final_score), 2) AS highest_score,
    ROUND(MIN(g.final_score), 2) AS lowest_score,
    ROUND(AVG(a.attendance_percentage), 2) AS avg_attendance
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
LEFT JOIN grades g ON e.id = g.enrollment_id
LEFT JOIN attendance a ON e.id = a.enrollment_id
GROUP BY c.id, c.course_name, c.major, c.duration_months
ORDER BY avg_final_score DESC;



-- SECTION 3: VIEWS


-- View 1: Student Transcript
-- Shows each student's full academic record across all courses

CREATE OR REPLACE VIEW vw_student_transcript AS
SELECT
    s.id AS student_id,
    s.name,
    s.surname,
    s.email,
    c.course_name,
    c.major,
    g.assignment_grade,
    g.exam_grade,
    g.final_score,
    CASE
        WHEN g.final_score >= 90 THEN 'A'
        WHEN g.final_score >= 80 THEN 'B'
        WHEN g.final_score >= 70 THEN 'C'
        WHEN g.final_score >= 60 THEN 'D'
        ELSE 'F'
    END AS letter_grade,
    CASE
        WHEN g.final_score >= 90 THEN 4.0
        WHEN g.final_score >= 80 THEN 3.0
        WHEN g.final_score >= 70 THEN 2.0
        WHEN g.final_score >= 60 THEN 1.0
        ELSE 0.0
    END AS gpa_points
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id
JOIN grades g ON e.id = g.enrollment_id
ORDER BY s.surname, s.name, c.course_name;


-- View 2: Course Roster
-- Shows all students currently enrolled in each course

CREATE OR REPLACE VIEW vw_course_roster AS
SELECT
    c.id AS course_id,
    c.course_name,
    c.major,
    s.id AS student_id,
    s.name,
    s.surname,
    s.email,
    s.gender
FROM courses c
JOIN enrollments e ON c.id = e.course_id
JOIN students s ON e.student_id = s.id
ORDER BY c.course_name, s.surname, s.name;


-- View 3: Attendance Report
-- Shows attendance standing for every student in every course

CREATE OR REPLACE VIEW vw_attendance_report AS
SELECT
    s.id AS student_id,
    s.name,
    s.surname,
    c.course_name,
    a.attendance_percentage,
    CASE
        WHEN a.attendance_percentage >= 90 THEN 'Excellent'
        WHEN a.attendance_percentage >= 75 THEN 'Satisfactory'
        WHEN a.attendance_percentage >= 50 THEN 'At Risk'
        ELSE 'Critical'
    END AS attendance_standing
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id
JOIN attendance a ON e.id = a.enrollment_id
ORDER BY a.attendance_percentage ASC;



-- SECTION 4: STORED PROCEDURES


-- Procedure 1: Enroll a student into a course

DELIMITER 
$$
CREATE PROCEDURE enroll_student(
    IN p_student_id INT,
    IN p_course_id INT
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM enrollments
        WHERE student_id = p_student_id
        AND course_id = p_course_id
    ) THEN
        INSERT INTO enrollments (student_id, course_id)
        VALUES (p_student_id, p_course_id);
        SELECT 'Student enrolled successfully.' AS message;
    ELSE
        SELECT 'Student is already enrolled in this course.' AS message;
    END IF;
END
$$


DELIMITER ;


-- Procedure 2: Record a grade for an enrollment

DELIMITER 
$$
CREATE PROCEDURE record_grade(
    IN p_enrollment_id INT,
    IN p_assignment_grade DECIMAL(5,2),
    IN p_exam_grade DECIMAL(5,2),
    IN p_final_score DECIMAL(5,2)
)
BEGIN
    IF EXISTS (
        SELECT 1 FROM enrollments WHERE id = p_enrollment_id
    ) THEN
        INSERT INTO grades (
            enrollment_id,
            assignment_grade,
            exam_grade,
            final_score
        )
        VALUES (
            p_enrollment_id,
            p_assignment_grade,
            p_exam_grade,
            p_final_score
        );
        SELECT 'Grade recorded successfully.' AS message;
    ELSE
        SELECT 'Enrollment not found.' AS message;
    END IF;
END
$$


DELIMITER ;


-- Procedure 3: Record attendance for an enrollment

DELIMITER 
$$
CREATE PROCEDURE record_attendance(
    IN p_enrollment_id INT,
    IN p_attendance_percentage DECIMAL(5,2)
)
BEGIN
    IF EXISTS (
        SELECT 1 FROM enrollments WHERE id = p_enrollment_id
    ) THEN
        INSERT INTO attendance (
            enrollment_id,
            attendance_percentage
        )
        VALUES (
            p_enrollment_id,
            p_attendance_percentage
        );
        SELECT 'Attendance recorded successfully.' AS message;
    ELSE
        SELECT 'Enrollment not found.' AS message;
    END IF;
END
$$


DELIMITER ;
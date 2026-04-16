import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
from app.db_connection import get_connection


@st.cache_data
def get_all_students():
    conn = get_connection()
    query = """
        SELECT
            id,
            name,
            surname,
            email,
            date_of_birth,
            gender
        FROM students
        ORDER BY surname, name;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_all_courses():
    conn = get_connection()
    query = """
        SELECT
            id,
            course_name,
            major,
            duration_months
        FROM courses
        ORDER BY course_name;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_all_grades():
    conn = get_connection()
    query = """
        SELECT
            s.id AS student_id,
            s.name,
            s.surname,
            c.course_name,
            c.major,
            g.assignment_grade,
            g.exam_grade,
            g.final_score
        FROM grades g
        JOIN enrollments e ON g.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY s.surname, s.name;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_all_attendance():
    conn = get_connection()
    query = """
        SELECT
            s.id AS student_id,
            s.name,
            s.surname,
            c.course_name,
            c.major,
            a.attendance_percentage
        FROM attendance a
        JOIN enrollments e ON a.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY s.surname, s.name;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_overview_metrics():
    conn = get_connection()
    query = """
        SELECT
            (SELECT COUNT(*) FROM students) AS total_students,
            (SELECT COUNT(*) FROM courses) AS total_courses,
            (SELECT COUNT(*) FROM enrollments) AS total_enrollments,
            (SELECT ROUND(AVG(final_score)::numeric, 2) FROM grades) AS average_final_score,
            (SELECT ROUND(AVG(attendance_percentage)::numeric, 2) FROM attendance) AS average_attendance;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_enrollments_per_course():
    conn = get_connection()
    query = """
        SELECT
            c.course_name,
            c.major,
            COUNT(e.id) AS total_enrollments
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        GROUP BY c.course_name, c.major
        ORDER BY total_enrollments DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_grade_distribution():
    conn = get_connection()
    query = """
        SELECT
            final_score
        FROM grades
        ORDER BY final_score;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_attendance_distribution():
    conn = get_connection()
    query = """
        SELECT
            attendance_percentage
        FROM attendance
        ORDER BY attendance_percentage;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_gender_distribution():
    conn = get_connection()
    query = """
        SELECT
            gender,
            COUNT(*) AS total
        FROM students
        GROUP BY gender
        ORDER BY total DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_average_grades_per_course():
    conn = get_connection()
    query = """
        SELECT
            c.course_name,
            ROUND(AVG(g.assignment_grade)::numeric, 2) AS avg_assignment,
            ROUND(AVG(g.exam_grade)::numeric, 2) AS avg_exam,
            ROUND(AVG(g.final_score)::numeric, 2) AS avg_final
        FROM grades g
        JOIN enrollments e ON g.enrollment_id = e.id
        JOIN courses c ON e.course_id = c.id
        GROUP BY c.course_name
        ORDER BY avg_final DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_average_attendance_per_course():
    conn = get_connection()
    query = """
        SELECT
            c.course_name,
            ROUND(AVG(a.attendance_percentage)::numeric, 2) AS avg_attendance
        FROM attendance a
        JOIN enrollments e ON a.enrollment_id = e.id
        JOIN courses c ON e.course_id = c.id
        GROUP BY c.course_name
        ORDER BY avg_attendance DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
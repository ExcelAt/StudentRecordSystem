import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from pathlib import Path
import pandas as pd
from io import StringIO


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Reports — Student Record System",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS LOADER
# ============================================================

def load_css():
    css_path = Path(__file__).parent.parent / "styles" / "main.css"
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css()


# ============================================================
# IMPORTS
# ============================================================

from utils.auth import require_admin, get_current_user, logout_user
from components.metrics import (
    render_page_header,
    render_section_title,
)
from utils.data_loader import (
    get_all_students,
    get_all_courses,
    get_all_grades,
    get_all_attendance,
    get_enrollments_per_course,
    get_average_grades_per_course,
    get_average_attendance_per_course,
)


# ============================================================
# AUTHENTICATION
# ============================================================

require_admin()


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    user = get_current_user()
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="sidebar-logo-title">Student Record System</div>
                <div class="sidebar-logo-sub">Academic Management Platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                background: rgba(79,142,247,0.08);
                border-radius: 10px;
                border: 1px solid rgba(79,142,247,0.15);
            ">
                <div style="
                    color: rgba(255,255,255,0.5);
                    font-size: 0.7rem;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    margin-bottom: 0.2rem;
                ">Signed in as</div>
                <div style="
                    color: #ffffff;
                    font-size: 0.9rem;
                    font-weight: 600;
                ">{user["name"]} {user["surname"]}</div>
                <div style="
                    color: rgba(79,142,247,0.9);
                    font-size: 0.75rem;
                    margin-top: 0.1rem;
                ">{user["role"].capitalize()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign Out", use_container_width=True):
            logout_user()
            st.switch_page("main.py")


render_sidebar()


# ============================================================
# CSV CONVERSION HELPER
# ============================================================

def convert_to_csv(df):
    """
    Converts a DataFrame to a UTF-8 encoded CSV string
    suitable for download.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    bytes
    """
    return df.to_csv(index=False).encode("utf-8")


# ============================================================
# PAGE HEADER
# ============================================================

render_page_header(
    title="Reports",
    subtitle="Generate and export system reports as CSV files.",
)

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# LOAD ALL DATA
# ============================================================

with st.spinner("Loading report data..."):
    students_df = get_all_students()
    courses_df = get_all_courses()
    grades_df = get_all_grades()
    attendance_df = get_all_attendance()
    enrollments_df = get_enrollments_per_course()
    avg_grades_df = get_average_grades_per_course()
    avg_attendance_df = get_average_attendance_per_course()


# ============================================================
# STUDENT REPORTS
# ============================================================

render_section_title("Student Reports")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">Full Student Directory</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">All registered students including name, email,
        date of birth and gender.</div>
    """, unsafe_allow_html=True)

    export_students = students_df[
        ["id", "name", "surname", "email", "date_of_birth", "gender"]
    ].copy()
    export_students.columns = [
        "ID", "Name", "Surname", "Email", "Date of Birth", "Gender"
    ]

    st.download_button(
        label="Download Student Directory",
        data=convert_to_csv(export_students),
        file_name="student_directory.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">At Risk Students</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">Students with attendance below 75% across
        any enrolled course.</div>
    """, unsafe_allow_html=True)

    at_risk_df = attendance_df[
        attendance_df["attendance_percentage"] < 75
    ].copy().sort_values("attendance_percentage")

    export_at_risk = at_risk_df[
        ["name", "surname", "course_name", "major", "attendance_percentage"]
    ].copy()
    export_at_risk.columns = [
        "Name", "Surname", "Course", "Major", "Attendance (%)"
    ]

    st.download_button(
        label="Download At Risk Students",
        data=convert_to_csv(export_at_risk),
        file_name="at_risk_students.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# GRADE REPORTS
# ============================================================

render_section_title("Grade Reports")

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">Full Grades Report</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">All student grades including assignment, exam
        and final scores per course.</div>
    """, unsafe_allow_html=True)

    export_grades = grades_df[
        ["name", "surname", "course_name", "major",
         "assignment_grade", "exam_grade", "final_score"]
    ].copy()
    export_grades.columns = [
        "Name", "Surname", "Course", "Major",
        "Assignment", "Exam", "Final Score"
    ]

    st.download_button(
        label="Download Full Grades Report",
        data=convert_to_csv(export_grades),
        file_name="grades_report.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">Average Grades Per Course</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">Course level summary of average assignment,
        exam and final scores.</div>
    """, unsafe_allow_html=True)

    export_avg_grades = avg_grades_df.copy()
    export_avg_grades.columns = [
        "Course", "Avg Assignment", "Avg Exam", "Avg Final"
    ]

    st.download_button(
        label="Download Average Grades Per Course",
        data=convert_to_csv(export_avg_grades),
        file_name="average_grades_per_course.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# ATTENDANCE REPORTS
# ============================================================

render_section_title("Attendance Reports")

col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">Full Attendance Report</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">All student attendance records across
        every enrolled course.</div>
    """, unsafe_allow_html=True)

    export_attendance = attendance_df[
        ["name", "surname", "course_name", "major", "attendance_percentage"]
    ].copy()
    export_attendance.columns = [
        "Name", "Surname", "Course", "Major", "Attendance (%)"
    ]

    st.download_button(
        label="Download Full Attendance Report",
        data=convert_to_csv(export_attendance),
        file_name="attendance_report.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col6:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">Average Attendance Per Course</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">Course level summary of average attendance
        percentage across all enrolled students.</div>
    """, unsafe_allow_html=True)

    export_avg_attendance = avg_attendance_df.copy()
    export_avg_attendance.columns = ["Course", "Avg Attendance (%)"]

    st.download_button(
        label="Download Average Attendance Per Course",
        data=convert_to_csv(export_avg_attendance),
        file_name="average_attendance_per_course.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# ENROLLMENT REPORTS
# ============================================================

render_section_title("Enrollment Reports")

col7, col8 = st.columns(2)

with col7:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">Enrollments Per Course</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">Total number of students enrolled
        in each course.</div>
    """, unsafe_allow_html=True)

    export_enrollments = enrollments_df.copy()
    export_enrollments.columns = ["Course", "Major", "Total Enrollments"]

    st.download_button(
        label="Download Enrollments Per Course",
        data=convert_to_csv(export_enrollments),
        file_name="enrollments_per_course.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col8:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.4rem;
        ">Full Course Directory</div>
        <div style="
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
        ">All courses with their major field
        and duration in months.</div>
    """, unsafe_allow_html=True)

    export_courses = courses_df[
        ["id", "course_name", "major", "duration_months"]
    ].copy()
    export_courses.columns = [
        "ID", "Course Name", "Major", "Duration (Months)"
    ]

    st.download_button(
        label="Download Course Directory",
        data=convert_to_csv(export_courses),
        file_name="course_directory.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
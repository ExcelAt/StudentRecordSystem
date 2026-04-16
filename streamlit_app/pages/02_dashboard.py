import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Dashboard — Student Record System",
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

from utils.auth import (
    require_authentication,
    is_admin,
    is_student,
    get_current_user,
    logout_user,
)
from components.metrics import (
    render_page_header,
    render_metric_row,
    render_section_title,
)
from utils.data_loader import (
    get_overview_metrics,
    get_all_students,
    get_all_courses,
    get_all_grades,
    get_all_attendance,
)


# ============================================================
# AUTHENTICATION CHECK
# ============================================================

require_authentication()


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

        st.markdown(
            """
            <div style="
                padding: 0.5rem 1rem;
                margin-bottom: 0.25rem;
            ">
                <p style="
                    color: rgba(255,255,255,0.35);
                    font-size: 0.7rem;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    font-weight: 500;
                    margin: 0;
                ">Navigation</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Sign Out", use_container_width=True):
            logout_user()
            st.switch_page("main.py")


render_sidebar()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def render_admin_dashboard():
    render_page_header(
        title="Admin Dashboard",
        subtitle="System wide overview of all students, courses, grades and attendance.",
    )

    with st.spinner("Loading system metrics..."):
        metrics_df = get_overview_metrics()

    if not metrics_df.empty:
        row = metrics_df.iloc[0]
        render_metric_row([
            {
                "label": "Total Students",
                "value": f"{int(row['total_students']):,}",
                "sub": "Registered",
            },
            {
                "label": "Total Courses",
                "value": f"{int(row['total_courses']):,}",
                "sub": "Active",
            },
            {
                "label": "Total Enrollments",
                "value": f"{int(row['total_enrollments']):,}",
                "sub": "Across All Courses",
            },
            {
                "label": "Average Final Score",
                "value": f"{float(row['average_final_score']):.1f}",
                "sub": "Out of 100",
            },
            {
                "label": "Average Attendance",
                "value": f"{float(row['average_attendance']):.1f}%",
                "sub": "Across All Courses",
            },
        ])

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # RECENT STUDENTS
    # --------------------------------------------------------

    render_section_title("Student Directory")

    with st.spinner("Loading students..."):
        students_df = get_all_students()

    col_search, col_gender, col_spacer = st.columns([2, 1, 2])

    with col_search:
        search_query = st.text_input(
            label="Search students",
            placeholder="Search by name, surname or email...",
            label_visibility="collapsed",
        )

    with col_gender:
        gender_options = ["All Genders"] + sorted(
            students_df["gender"].dropna().unique().tolist()
        )
        selected_gender = st.selectbox(
            label="Filter by gender",
            options=gender_options,
            label_visibility="collapsed",
        )

    filtered_students = students_df.copy()

    if search_query:
        query_lower = search_query.lower()
        filtered_students = filtered_students[
            filtered_students["name"].str.lower().str.contains(query_lower, na=False)
            | filtered_students["surname"].str.lower().str.contains(query_lower, na=False)
            | filtered_students["email"].str.lower().str.contains(query_lower, na=False)
        ]

    if selected_gender != "All Genders":
        filtered_students = filtered_students[
            filtered_students["gender"].str.lower() == selected_gender.lower()
        ]

    st.markdown(
        f"""
        <div style="
            color: rgba(255,255,255,0.45);
            font-size: 0.8rem;
            margin-bottom: 0.75rem;
            margin-top: 0.5rem;
        ">
            Showing {len(filtered_students):,} of {len(students_df):,} students
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    display_df = filtered_students[
        ["id", "name", "surname", "email", "date_of_birth", "gender"]
    ].copy()
    display_df.columns = ["ID", "Name", "Surname", "Email", "Date of Birth", "Gender"]

    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # COURSES
    # --------------------------------------------------------

    render_section_title("Course Directory")

    with st.spinner("Loading courses..."):
        courses_df = get_all_courses()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    display_courses = courses_df[
        ["id", "course_name", "major", "duration_months"]
    ].copy()
    display_courses.columns = ["ID", "Course Name", "Major", "Duration (Months)"]

    st.dataframe(display_courses, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # GRADES
    # --------------------------------------------------------

    render_section_title("Grades Overview")

    with st.spinner("Loading grades..."):
        grades_df = get_all_grades()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    display_grades = grades_df[
        ["name", "surname", "course_name", "assignment_grade", "exam_grade", "final_score"]
    ].copy()
    display_grades.columns = [
        "Name", "Surname", "Course", "Assignment", "Exam", "Final Score"
    ]

    st.dataframe(display_grades, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    render_section_title("Attendance Overview")

    with st.spinner("Loading attendance..."):
        attendance_df = get_all_attendance()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    display_attendance = attendance_df[
        ["name", "surname", "course_name", "attendance_percentage"]
    ].copy()
    display_attendance.columns = ["Name", "Surname", "Course", "Attendance (%)"]

    st.dataframe(display_attendance, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# STUDENT DASHBOARD
# ============================================================

def render_student_dashboard():
    user = get_current_user()

    render_page_header(
        title=f"Welcome, {user['name']}",
        subtitle="Your personal academic summary.",
    )

    student_id = user["student_id"]

    with st.spinner("Loading your records..."):
        grades_df = get_all_grades()
        attendance_df = get_all_attendance()

    my_grades = grades_df[grades_df["student_id"] == student_id].copy()
    my_attendance = attendance_df[attendance_df["student_id"] == student_id].copy()

    # --------------------------------------------------------
    # STUDENT METRICS
    # --------------------------------------------------------

    avg_final = my_grades["final_score"].mean() if not my_grades.empty else 0
    avg_attendance = my_attendance["attendance_percentage"].mean() if not my_attendance.empty else 0
    total_courses = len(my_grades)

    render_metric_row([
        {
            "label": "Courses Enrolled",
            "value": f"{total_courses}",
            "sub": "Active Enrollments",
        },
        {
            "label": "Average Final Score",
            "value": f"{avg_final:.1f}",
            "sub": "Out of 100",
        },
        {
            "label": "Average Attendance",
            "value": f"{avg_attendance:.1f}%",
            "sub": "Across All Courses",
        },
    ])

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # MY GRADES
    # --------------------------------------------------------

    render_section_title("My Grades")

    if my_grades.empty:
        st.info("No grade records found for your account.")
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        display_grades = my_grades[
            ["course_name", "major", "assignment_grade", "exam_grade", "final_score"]
        ].copy()
        display_grades.columns = [
            "Course", "Major", "Assignment", "Exam", "Final Score"
        ]

        st.dataframe(display_grades, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # MY ATTENDANCE
    # --------------------------------------------------------

    render_section_title("My Attendance")

    if my_attendance.empty:
        st.info("No attendance records found for your account.")
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        display_attendance = my_attendance[
            ["course_name", "major", "attendance_percentage"]
        ].copy()
        display_attendance.columns = ["Course", "Major", "Attendance (%)"]

        st.dataframe(display_attendance, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RENDER BASED ON ROLE
# ============================================================

if is_admin():
    render_admin_dashboard()
elif is_student():
    render_student_dashboard()
else:
    st.error("Your account role is not recognized. Please contact the administrator.")
    st.stop()
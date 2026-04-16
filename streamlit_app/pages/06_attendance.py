import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Attendance — Student Record System",
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
    render_metric_row,
    render_section_title,
)
from utils.data_loader import get_all_attendance, get_all_students, get_all_courses
from app.db_connection import get_connection


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
# RECORD ATTENDANCE FUNCTION
# ============================================================

def record_attendance(enrollment_id, attendance_percentage):
    """
    Inserts or updates an attendance record for a given enrollment.

    Parameters
    ----------
    enrollment_id : int
    attendance_percentage : float
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance (enrollment_id, attendance_percentage)
        VALUES (%s, %s)
        ON CONFLICT (enrollment_id)
        DO UPDATE SET
            attendance_percentage = EXCLUDED.attendance_percentage;
    """, (enrollment_id, attendance_percentage))

    conn.commit()
    cursor.close()
    conn.close()


def get_enrollment_id(student_id, course_id):
    """
    Retrieves the enrollment id for a given student and course.

    Parameters
    ----------
    student_id : int
    course_id : int

    Returns
    -------
    int or None
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM enrollments
        WHERE student_id = %s AND course_id = %s;
    """, (student_id, course_id))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result[0] if result else None


# ============================================================
# PAGE HEADER
# ============================================================

render_page_header(
    title="Attendance",
    subtitle="Record and manage student attendance across all courses.",
)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Loading attendance records..."):
    attendance_df = get_all_attendance()
    students_df = get_all_students()
    courses_df = get_all_courses()

total_records = len(attendance_df)
avg_attendance = attendance_df["attendance_percentage"].mean()
below_75 = len(attendance_df[attendance_df["attendance_percentage"] < 75])
above_75 = len(attendance_df[attendance_df["attendance_percentage"] >= 75])

render_metric_row([
    {
        "label": "Total Records",
        "value": f"{total_records:,}",
        "sub": "Across All Enrollments",
    },
    {
        "label": "Average Attendance",
        "value": f"{avg_attendance:.1f}%",
        "sub": "Across All Courses",
    },
    {
        "label": "Below 75%",
        "value": f"{below_75:,}",
        "sub": "At Risk Students",
    },
    {
        "label": "Above 75%",
        "value": f"{above_75:,}",
        "sub": "Satisfactory Attendance",
    },
])

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# RECORD ATTENDANCE FORM
# ============================================================

render_section_title("Record Attendance")

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

student_options = {
    f"{row['name']} {row['surname']} ({row['email']})": row["id"]
    for _, row in students_df.iterrows()
}

course_options = {
    row["course_name"]: row["id"]
    for _, row in courses_df.iterrows()
}

with st.form(key="record_attendance_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_student_label = st.selectbox(
            "Select Student",
            options=list(student_options.keys()),
        )

    with col2:
        selected_course_label = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
        )

    with col3:
        attendance_percentage = st.number_input(
            "Attendance Percentage",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5,
        )

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    submitted = st.form_submit_button(
        "Record Attendance",
        use_container_width=True,
    )

    if submitted:
        student_id = student_options[selected_student_label]
        course_id = course_options[selected_course_label]
        enrollment_id = get_enrollment_id(student_id, course_id)

        if enrollment_id is None:
            st.error(
                "This student is not enrolled in the selected course. "
                "Please enroll the student first."
            )
        else:
            try:
                record_attendance(
                    enrollment_id=enrollment_id,
                    attendance_percentage=attendance_percentage,
                )
                st.success("Attendance recorded successfully.")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Failed to record attendance. {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# AT RISK STUDENTS
# ============================================================

render_section_title("At Risk Students — Below 75% Attendance")

at_risk_df = attendance_df[
    attendance_df["attendance_percentage"] < 75
].copy().sort_values("attendance_percentage")

if at_risk_df.empty:
    st.info("No students are currently below the 75% attendance threshold.")
else:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    display_at_risk = at_risk_df[
        ["name", "surname", "course_name", "major", "attendance_percentage"]
    ].copy()
    display_at_risk.columns = [
        "Name", "Surname", "Course", "Major", "Attendance (%)"
    ]

    st.dataframe(display_at_risk, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# FULL ATTENDANCE DIRECTORY
# ============================================================

render_section_title("Full Attendance Directory")

col_search, col_spacer = st.columns([2, 3])

with col_search:
    search_query = st.text_input(
        label="Search attendance",
        placeholder="Search by student name or course...",
        label_visibility="collapsed",
    )

filtered_df = attendance_df.copy()

if search_query:
    query_lower = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["name"].str.lower().str.contains(query_lower, na=False)
        | filtered_df["surname"].str.lower().str.contains(query_lower, na=False)
        | filtered_df["course_name"].str.lower().str.contains(query_lower, na=False)
    ]

st.markdown(
    f"""
    <div style="
        color: rgba(255,255,255,0.45);
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
        margin-top: 0.5rem;
    ">
        Showing {len(filtered_df):,} of {total_records:,} attendance records
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

display_df = filtered_df[
    ["name", "surname", "course_name", "major", "attendance_percentage"]
].copy()
display_df.columns = ["Name", "Surname", "Course", "Major", "Attendance (%)"]

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("</div>", unsafe_allow_html=True)
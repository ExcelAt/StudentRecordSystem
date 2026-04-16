import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Grades — Student Record System",
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
from utils.data_loader import get_all_grades, get_all_students, get_all_courses
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
# RECORD GRADE FUNCTION
# ============================================================

def record_grade(enrollment_id, assignment_grade, exam_grade):
    """
    Inserts or updates a grade record for a given enrollment.

    Parameters
    ----------
    enrollment_id : int
    assignment_grade : float
    exam_grade : float
    """
    final_score = round((assignment_grade * 0.4) + (exam_grade * 0.6), 2)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO grades (enrollment_id, assignment_grade, exam_grade, final_score)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (enrollment_id)
        DO UPDATE SET
            assignment_grade = EXCLUDED.assignment_grade,
            exam_grade = EXCLUDED.exam_grade,
            final_score = EXCLUDED.final_score;
    """, (enrollment_id, assignment_grade, exam_grade, final_score))

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
    title="Grades",
    subtitle="Record and manage student grades across all courses.",
)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Loading grades..."):
    grades_df = get_all_grades()
    students_df = get_all_students()
    courses_df = get_all_courses()

total_records = len(grades_df)
avg_assignment = grades_df["assignment_grade"].mean()
avg_exam = grades_df["exam_grade"].mean()
avg_final = grades_df["final_score"].mean()

render_metric_row([
    {
        "label": "Total Grade Records",
        "value": f"{total_records:,}",
        "sub": "Across All Enrollments",
    },
    {
        "label": "Average Assignment",
        "value": f"{avg_assignment:.1f}",
        "sub": "Out of 100",
    },
    {
        "label": "Average Exam",
        "value": f"{avg_exam:.1f}",
        "sub": "Out of 100",
    },
    {
        "label": "Average Final Score",
        "value": f"{avg_final:.1f}",
        "sub": "Out of 100",
    },
])

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# RECORD GRADE FORM
# ============================================================

render_section_title("Record Grade")

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

student_options = {
    f"{row['name']} {row['surname']} ({row['email']})": row["id"]
    for _, row in students_df.iterrows()
}

course_options = {
    row["course_name"]: row["id"]
    for _, row in courses_df.iterrows()
}

with st.form(key="record_grade_form"):
    col1, col2 = st.columns(2)

    with col1:
        selected_student_label = st.selectbox(
            "Select Student",
            options=list(student_options.keys()),
        )
        assignment_grade = st.number_input(
            "Assignment Grade",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5,
        )

    with col2:
        selected_course_label = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
        )
        exam_grade = st.number_input(
            "Exam Grade",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5,
        )

    final_preview = round((assignment_grade * 0.4) + (exam_grade * 0.6), 2)

    st.markdown(
        f"""
        <div style="
            color: rgba(255,255,255,0.5);
            font-size: 0.85rem;
            margin-top: 0.5rem;
        ">
            Calculated Final Score: 
            <span style="color: #4f8ef7; font-weight: 600;">
                {final_preview}
            </span>
            (Assignment 40% + Exam 60%)
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    submitted = st.form_submit_button("Record Grade", use_container_width=True)

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
                record_grade(
                    enrollment_id=enrollment_id,
                    assignment_grade=assignment_grade,
                    exam_grade=exam_grade,
                )
                st.success(
                    f"Grade recorded successfully. Final score: {final_preview}"
                )
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Failed to record grade. {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# GRADES DIRECTORY
# ============================================================

render_section_title("Grades Directory")

col_search, col_spacer = st.columns([2, 3])

with col_search:
    search_query = st.text_input(
        label="Search grades",
        placeholder="Search by student name or course...",
        label_visibility="collapsed",
    )

filtered_df = grades_df.copy()

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
        Showing {len(filtered_df):,} of {total_records:,} grade records
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

display_df = filtered_df[
    ["name", "surname", "course_name", "major",
     "assignment_grade", "exam_grade", "final_score"]
].copy()
display_df.columns = [
    "Name", "Surname", "Course", "Major",
    "Assignment", "Exam", "Final Score"
]

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("</div>", unsafe_allow_html=True)
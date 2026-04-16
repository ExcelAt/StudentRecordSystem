import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Courses — Student Record System",
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
from utils.data_loader import get_all_courses, get_enrollments_per_course
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
# ADD COURSE FUNCTION
# ============================================================

def add_course(course_name, major, duration_months):
    """
    Inserts a new course record into the courses table.

    Parameters
    ----------
    course_name : str
    major : str
    duration_months : int
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO courses (course_name, major, duration_months)
        VALUES (%s, %s, %s);
    """, (course_name, major, duration_months))

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# PAGE HEADER
# ============================================================

render_page_header(
    title="Courses",
    subtitle="View, search and add courses to the system.",
)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Loading courses..."):
    courses_df = get_all_courses()
    enrollments_df = get_enrollments_per_course()

total_courses = len(courses_df)
total_majors = courses_df["major"].nunique()
avg_duration = courses_df["duration_months"].mean()

render_metric_row([
    {
        "label": "Total Courses",
        "value": f"{total_courses:,}",
        "sub": "Active",
    },
    {
        "label": "Total Majors",
        "value": f"{total_majors:,}",
        "sub": "Distinct Fields",
    },
    {
        "label": "Average Duration",
        "value": f"{avg_duration:.1f}",
        "sub": "Months",
    },
])

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# ADD NEW COURSE FORM
# ============================================================

render_section_title("Add New Course")

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

with st.form(key="add_course_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        new_course_name = st.text_input(
            "Course Name",
            placeholder="Enter course name",
        )

    with col2:
        new_major = st.text_input(
            "Major",
            placeholder="Enter major field",
        )

    with col3:
        new_duration = st.number_input(
            "Duration (Months)",
            min_value=1,
            max_value=60,
            value=12,
        )

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    submitted = st.form_submit_button("Add Course", use_container_width=True)

    if submitted:
        if not new_course_name or not new_major:
            st.error("Please fill in all required fields.")
        else:
            try:
                add_course(
                    course_name=new_course_name.strip(),
                    major=new_major.strip(),
                    duration_months=int(new_duration),
                )
                st.success(
                    f"Course '{new_course_name}' added successfully."
                )
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Failed to add course. {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# COURSE DIRECTORY
# ============================================================

render_section_title("Course Directory")

col_search, col_major, col_spacer = st.columns([2, 1, 2])

with col_search:
    search_query = st.text_input(
        label="Search courses",
        placeholder="Search by course name or major...",
        label_visibility="collapsed",
    )

with col_major:
    major_options = ["All Majors"] + sorted(
        courses_df["major"].dropna().unique().tolist()
    )
    selected_major = st.selectbox(
        label="Filter by major",
        options=major_options,
        label_visibility="collapsed",
    )

filtered_df = courses_df.copy()

if search_query:
    query_lower = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["course_name"].str.lower().str.contains(query_lower, na=False)
        | filtered_df["major"].str.lower().str.contains(query_lower, na=False)
    ]

if selected_major != "All Majors":
    filtered_df = filtered_df[
        filtered_df["major"].str.lower() == selected_major.lower()
    ]

st.markdown(
    f"""
    <div style="
        color: rgba(255,255,255,0.45);
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
        margin-top: 0.5rem;
    ">
        Showing {len(filtered_df):,} of {total_courses:,} courses
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

display_df = filtered_df[
    ["id", "course_name", "major", "duration_months"]
].copy()
display_df.columns = ["ID", "Course Name", "Major", "Duration (Months)"]

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# ENROLLMENT SUMMARY
# ============================================================

render_section_title("Enrollment Summary Per Course")

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

display_enrollments = enrollments_df[
    ["course_name", "major", "total_enrollments"]
].copy()
display_enrollments.columns = ["Course Name", "Major", "Total Enrollments"]

st.dataframe(display_enrollments, use_container_width=True, hide_index=True)

st.markdown("</div>", unsafe_allow_html=True)
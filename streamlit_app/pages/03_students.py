import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from pathlib import Path
from datetime import date


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Students — Student Record System",
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
from utils.data_loader import get_all_students
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
# ADD STUDENT FUNCTION
# ============================================================

def add_student(name, surname, email, date_of_birth, gender):
    """
    Inserts a new student record into the students table
    and creates a corresponding user account.

    Parameters
    ----------
    name : str
    surname : str
    email : str
    date_of_birth : date
    gender : str
    """
    import bcrypt

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (name, surname, email, date_of_birth, gender)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (name, surname, email, date_of_birth, gender))

    new_student_id = cursor.fetchone()[0]

    password_hash = bcrypt.hashpw(
        "Student@2025".encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute("""
        INSERT INTO users (student_id, email, password_hash, role)
        VALUES (%s, %s, %s, 'student')
        ON CONFLICT (email) DO NOTHING;
    """, (new_student_id, email, password_hash))

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# PAGE HEADER
# ============================================================

render_page_header(
    title="Students",
    subtitle="View, search and add students to the system.",
)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Loading students..."):
    students_df = get_all_students()

total_students = len(students_df)
total_male = len(students_df[students_df["gender"].str.lower() == "male"])
total_female = len(students_df[students_df["gender"].str.lower() == "female"])

render_metric_row([
    {
        "label": "Total Students",
        "value": f"{total_students:,}",
        "sub": "Registered",
    },
    {
        "label": "Male Students",
        "value": f"{total_male:,}",
        "sub": f"{(total_male / total_students * 100):.1f}% of total",
    },
    {
        "label": "Female Students",
        "value": f"{total_female:,}",
        "sub": f"{(total_female / total_students * 100):.1f}% of total",
    },
])

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# ADD NEW STUDENT FORM
# ============================================================

render_section_title("Add New Student")

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

with st.form(key="add_student_form"):
    col1, col2 = st.columns(2)

    with col1:
        new_name = st.text_input("First Name", placeholder="Enter first name")
        new_email = st.text_input("Email Address", placeholder="Enter email address")
        new_gender = st.selectbox("Gender", options=["Male", "Female"])

    with col2:
        new_surname = st.text_input("Surname", placeholder="Enter surname")
        new_dob = st.date_input(
            "Date of Birth",
            min_value=date(1950, 1, 1),
            max_value=date.today(),
        )

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    submitted = st.form_submit_button("Add Student", use_container_width=True)

    if submitted:
        if not new_name or not new_surname or not new_email:
            st.error("Please fill in all required fields.")
        else:
            try:
                add_student(
                    name=new_name.strip(),
                    surname=new_surname.strip(),
                    email=new_email.strip().lower(),
                    date_of_birth=new_dob,
                    gender=new_gender,
                )
                st.success(
                    f"Student {new_name} {new_surname} added successfully. "
                    f"Their login password is Student@2025."
                )
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Failed to add student. {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# STUDENT DIRECTORY
# ============================================================

render_section_title("Student Directory")

col_search, col_gender, col_spacer = st.columns([2, 1, 2])

with col_search:
    search_query = st.text_input(
        label="Search",
        placeholder="Search by name, surname or email...",
        label_visibility="collapsed",
    )

with col_gender:
    gender_options = ["All Genders"] + sorted(
        students_df["gender"].dropna().unique().tolist()
    )
    selected_gender = st.selectbox(
        label="Gender",
        options=gender_options,
        label_visibility="collapsed",
    )

filtered_df = students_df.copy()

if search_query:
    query_lower = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["name"].str.lower().str.contains(query_lower, na=False)
        | filtered_df["surname"].str.lower().str.contains(query_lower, na=False)
        | filtered_df["email"].str.lower().str.contains(query_lower, na=False)
    ]

if selected_gender != "All Genders":
    filtered_df = filtered_df[
        filtered_df["gender"].str.lower() == selected_gender.lower()
    ]

st.markdown(
    f"""
    <div style="
        color: rgba(255,255,255,0.45);
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
        margin-top: 0.5rem;
    ">
        Showing {len(filtered_df):,} of {total_students:,} students
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

display_df = filtered_df[
    ["id", "name", "surname", "email", "date_of_birth", "gender"]
].copy()
display_df.columns = ["ID", "Name", "Surname", "Email", "Date of Birth", "Gender"]

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("</div>", unsafe_allow_html=True)
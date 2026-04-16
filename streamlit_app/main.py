import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="Student Record System",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)


def load_css():
    css_path = Path(__file__).parent / "styles" / "main.css"
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css()


st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)


from utils.auth import verify_login, login_user, is_authenticated

if is_authenticated():
    st.switch_page("pages/02_dashboard.py")


st.markdown("""
    <div style="
        text-align: center;
        padding: 3rem 0 2rem 0;
    ">
        <div style="
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.02em;
            margin-bottom: 0.3rem;
        ">Student Record System</div>
        <div style="
            font-size: 0.9rem;
            color: rgba(255,255,255,0.45);
        ">Academic Management Platform</div>
    </div>
""", unsafe_allow_html=True)


with st.form(key="login_form"):
    st.markdown("""
        <div style="
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.5rem;
        ">Sign In</div>
    """, unsafe_allow_html=True)

    email = st.text_input(
        label="Email Address",
        placeholder="Enter your email address",
    )
    password = st.text_input(
        label="Password",
        placeholder="Enter your password",
        type="password",
    )

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    submit = st.form_submit_button(
        label="Sign In",
        use_container_width=True,
    )

if submit:
    if not email or not password:
        st.error("Please enter both your email address and password.")
    else:
        with st.spinner("Verifying credentials..."):
            user_data = verify_login(email, password)

        if user_data is None:
            st.error("Incorrect email address or password. Please try again.")
        else:
            login_user(user_data)
            st.success(f"Welcome back, {user_data['name']}.")
            st.switch_page("pages/02_dashboard.py")


st.markdown("""
    <div style="
        text-align: center;
        margin-top: 2rem;
        color: rgba(255,255,255,0.25);
        font-size: 0.75rem;
    ">
        Student Record System — Academic Management Platform
    </div>
""", unsafe_allow_html=True)
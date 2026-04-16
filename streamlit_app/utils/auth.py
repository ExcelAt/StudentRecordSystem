import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import bcrypt
from app.db_connection import get_connection
import streamlit as st


# ============================================================
# AUTHENTICATION
# ============================================================

def verify_login(email, password):
    """
    Verifies a user's email and password against the database.

    Parameters
    ----------
    email : str
        The email address entered by the user.
    password : str
        The plain text password entered by the user.

    Returns
    -------
    dict or None
        A dictionary containing user details if credentials
        are valid, otherwise None.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            u.id,
            u.email,
            u.password_hash,
            u.role,
            u.student_id,
            s.name,
            s.surname
        FROM users u
        LEFT JOIN students s ON u.student_id = s.id
        WHERE u.email = %s;
    """, (email.strip().lower(),))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result is None:
        return None

    user_id, db_email, password_hash, role, student_id, name, surname = result

    password_matches = bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )

    if not password_matches:
        return None

    return {
    "user_id": user_id,
    "email": db_email,
    "role": role,
    "student_id": student_id,
    "name": name if name else "Admin",
    "surname": surname if surname else "",
}

# ============================================================
# SESSION STATE HELPERS
# ============================================================

def login_user(user_data):
    """
    Stores authenticated user data in Streamlit session state.

    Parameters
    ----------
    user_data : dict
        The user dictionary returned by verify_login.
    """
    st.session_state["authenticated"] = True
    st.session_state["user"] = user_data


def logout_user():
    """
    Clears all authentication data from session state.
    """
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state.clear()


def is_authenticated():
    """
    Returns True if the current session has an authenticated user.

    Returns
    -------
    bool
    """
    return st.session_state.get("authenticated", False)


def get_current_user():
    """
    Returns the currently authenticated user dictionary.

    Returns
    -------
    dict or None
    """
    return st.session_state.get("user", None)


def is_admin():
    """
    Returns True if the current authenticated user has the admin role.

    Returns
    -------
    bool
    """
    user = get_current_user()
    if user is None:
        return False
    return user.get("role") == "admin"


def is_student():
    """
    Returns True if the current authenticated user has the student role.

    Returns
    -------
    bool
    """
    user = get_current_user()
    if user is None:
        return False
    return user.get("role") == "student"


# ============================================================
# ACCESS CONTROL
# ============================================================

def require_authentication():
    """
    Redirects unauthenticated users to the login page.
    Call this at the top of every protected page.
    """
    if not is_authenticated():
        st.switch_page("main.py")
        st.stop()


def require_admin():
    """
    Blocks access to admin-only pages for non-admin users.
    Call this at the top of every admin-only page.
    """
    require_authentication()
    if not is_admin():
        st.error("You do not have permission to view this page.")
        st.stop()
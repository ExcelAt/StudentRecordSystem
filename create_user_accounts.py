import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import bcrypt
from app.db_connection import get_connection


def hash_password(plain_text_password):
    """
    Hashes a plain text password using bcrypt.

    Parameters
    ----------
    plain_text_password : str
        The plain text password to hash.

    Returns
    -------
    str
        The hashed password string.
    """
    return bcrypt.hashpw(
        plain_text_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def create_admin_account(cursor):
    """
    Creates a single admin account.
    Email: admin@studentrecords.com
    Password: Admin@2025
    """
    email = "admin@studentrecords.com"
    password_hash = hash_password("Admin@2025")

    cursor.execute("""
        INSERT INTO users (student_id, email, password_hash, role)
        VALUES (NULL, %s, %s, 'admin')
        ON CONFLICT (email) DO NOTHING;
    """, (email, password_hash))

    print("Admin account created.")
    print("  Email   : admin@studentrecords.com")
    print("  Password: Admin@2025")


def create_student_accounts(cursor):
    """
    Creates one user account for every student in the
    students table. Each student logs in with their
    existing email address and a default password.
    Default password: Student@2025
    """
    cursor.execute("""
        SELECT id, email FROM students ORDER BY id;
    """)
    students = cursor.fetchall()

    default_password_hash = hash_password("Student@2025")

    created = 0
    skipped = 0

    for student_id, email in students:
        cursor.execute("""
            INSERT INTO users (student_id, email, password_hash, role)
            VALUES (%s, %s, %s, 'student')
            ON CONFLICT (email) DO NOTHING;
        """, (student_id, email, default_password_hash))

        if cursor.rowcount > 0:
            created += 1
        else:
            skipped += 1

    print(f"Student accounts created : {created}")
    print(f"Student accounts skipped : {skipped} (already existed)")


def main():
    conn = get_connection()
    cursor = conn.cursor()

    print("Creating admin account...")
    create_admin_account(cursor)

    print("\nCreating student accounts...")
    create_student_accounts(cursor)

    conn.commit()
    cursor.close()
    conn.close()

    print("\nAll accounts created successfully.")
    print("\nDefault credentials:")
    print("  Admin   — admin@studentrecords.com / Admin@2025")
    print("  Student — their registered email / Student@2025")


if __name__ == "__main__":
    main()
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    try:
        import streamlit as st
        host = st.secrets["DB_HOST"]
        user = st.secrets["DB_USER"]
        password = st.secrets["DB_PASSWORD"]
        dbname = st.secrets["DB_NAME"]
        sslmode = st.secrets["DB_SSLMODE"]
    except Exception:
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        dbname = os.getenv("DB_NAME")
        sslmode = os.getenv("DB_SSLMODE")

    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=dbname,
        sslmode=sslmode,
    )
    return conn
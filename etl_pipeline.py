import pandas as pd
import psycopg2
import re
import logging

# ---------------- CONFIG ----------------
DB_CONFIG = {
    "host": "studentrecordsdb.postgres.database.azure.com",
    "user": "exceladmin",
    "password": "Abracadabra@1",
    "dbname": "student_record_system",
    "sslmode": "require"
}
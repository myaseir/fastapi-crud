import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator

DB_HOST = "localhost"
DB_NAME = "fastapi_db"
DB_USER = "fastapi_user"
DB_PASS = "admin"

def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=RealDictCursor
    )
    return conn

# ✅ FastAPI-compatible database dependency
def get_db() -> Generator:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

from db import get_connection
from schemas import UserCreate, User
import random
import string
import bcrypt
from psycopg2.extras import RealDictCursor


def generate_vending_code(length=5):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# Google user creation or fetch
def create_user_if_not_exists(conn, user: UserCreate):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user.id,))
        existing = cur.fetchone()
        if existing:
            return existing

        vending_code = generate_vending_code()

        cur.execute(
            """
            INSERT INTO users (id, name, email, vending_code, balance, recent_usage, auth_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                user.id,
                user.name,
                user.email,
                vending_code,
                user.balance or 0,
                "",  # recent_usage default
                "google"
            )
        )
        conn.commit()
        return cur.fetchone()


# Manual registration
def create_manual_user(conn, full_name, email, password):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return None  # Already exists

        user_id = generate_vending_code() + "_" + ''.join(random.choices(string.digits, k=5))
        vending_code = generate_vending_code()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cur.execute(
            """
            INSERT INTO users (id, name, email, password_hash, vending_code, balance, recent_usage, auth_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                user_id,
                full_name,
                email,
                password_hash,
                vending_code,
                0,
                "",
                "manual"
            )
        )
        conn.commit()
        return cur.fetchone()


# All users
def get_users():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()


# Single user by ID
def get_user(user_id: str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()


# Create user manually if needed (not used for Google users)
def create_user(user: UserCreate):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO users (id, name, email, vending_code, balance, recent_usage, auth_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    user.id,
                    user.name,
                    user.email,
                    user.vending_code,
                    user.balance or 0,
                    "",
                    "manual"
                )
            )
            conn.commit()
            return cur.fetchone()


# Update user
def update_user(user_id: str, user: UserCreate):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE users
                SET name = %s, email = %s, vending_code = %s, balance = %s
                WHERE id = %s
                RETURNING *
                """,
                (user.name, user.email, user.vending_code, user.balance, user_id)
            )
            conn.commit()
            return cur.fetchone()


# Delete user
def delete_user(user_id: str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("DELETE FROM users WHERE id = %s RETURNING *", (user_id,))
            conn.commit()
            return cur.fetchone()

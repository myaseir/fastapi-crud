from psycopg2.extras import RealDictCursor
from schemas import ManualRegisterCreate, RegisterOut, UserCreate

from db import get_connection
import bcrypt
import crud


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_registration(conn, user: ManualRegisterCreate) -> RegisterOut:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check if email already exists
        cur.execute("SELECT * FROM register WHERE email = %s", (user.email,))
        existing = cur.fetchone()
        if existing:
            raise Exception("Email already registered")

        # Hash the password
        hashed = hash_password(user.password)

        # Insert into register table
        cur.execute(
            """
            INSERT INTO register (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, full_name, email
            """,
            (user.full_name, user.email, hashed)
        )
        reg_user = cur.fetchone()

        # Sync with `users` table
        user_id = str(reg_user['id'])  # ✅ keeps the same ID (e.g., "1")

        vending_code = crud.generate_vending_code()

        user_entry = UserCreate(
    id=user_id,
    name=reg_user['full_name'],
    email=reg_user['email'],
    vending_code=vending_code,
    balance=0.0,
    auth_type="manual"  # ✅ Add this line
)

        crud.create_user(user_entry)

        conn.commit()
        return reg_user


def get_all_registrations(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, full_name, email FROM register")
        return cur.fetchall()

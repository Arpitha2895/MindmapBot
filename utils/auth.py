import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mindmapbot.db")

def _connect():
    return sqlite3.connect(DB_PATH)

def _init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()

_init_db()

def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user(username, email, phone, password):
    username = username.strip()
    email = email.strip().lower()
    phone = phone.strip()

    if not username or not email or not password:
        return False, "Username, email and password are required."

    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO users (username,email,phone,password_hash) VALUES (?,?,?,?)",
                (username, email, phone, _hash_password(password))
            )
            conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as e:
        return False, "Registration failed: " + str(e)

def authenticate(login_id, password):
    login_id = login_id.strip().lower()
    with _connect() as conn:
        row = conn.execute(
            """SELECT id, username, email, phone
               FROM users
               WHERE (lower(email)=? OR phone=?)
                 AND password_hash=?""",
            (login_id, login_id, _hash_password(password))
        ).fetchone()

    if row:
        return True, "Login successful.", {
            "id": row[0], "username": row[1], "email": row[2], "phone": row[3]
        }
    return False, "Invalid email/phone or password.", None

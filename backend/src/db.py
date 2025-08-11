import sqlite3
import datetime
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "app.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Users
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    # Tabela spożycia
    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_intake (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        protein REAL,
        carbs REAL,
        fat REAL,
        calories REAL,
        description TEXT
    )""")
    # Historia celów
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_targets_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        protein REAL,
        carbs REAL,
        fat REAL,
        calories REAL
    )""")
    # Logi OpenAI
    cur.execute("""
    CREATE TABLE IF NOT EXISTS openai_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        prompt TEXT,
        response TEXT,
        response_time_ms INTEGER
    )""")
    # Users for auth
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT
    )""")
    # Pierwszy rekord domyślnych celów (jeśli brak historii)
    res = cur.execute("SELECT COUNT(*) FROM user_targets_history").fetchone()
    if res and res[0] == 0:
        cur.execute(
            "INSERT INTO user_targets_history (ts, protein, carbs, fat, calories) VALUES (?, ?, ?, ?, ?)",
            ("2000-01-01T00:00:00", 120, 195, 60, 1800)
        )
    conn.commit()
    conn.close()

"""
Bandhu AI - Database Persistence Service
========================================

Manages SQLite database operations (`bandhu_data.db`) for user settings 
and chat log auditing.
"""

import json
import logging
import os
import sqlite3

logger = logging.getLogger("bandhu.db")

# Path to SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bandhu_data.db")

# Default user preference profile settings
DEFAULT_SETTINGS = {
    "name": "संतोष जाधव",
    "phone": "+919876543210",
    "speech_speed": 1.0,
    "auto_play_speech": True,
    "notifications_enabled": True,
    "crop_alerts_enabled": True,
    "dark_mode": False,
    "save_history": True,
}


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a SQLite database connection with dict row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite database schema and inserts default settings row."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Settings table storing JSON settings payload
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY DEFAULT 1,
            data TEXT NOT NULL
        )
    """)

    # Chat history audit logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            category TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure row ID 1 exists with DEFAULT_SETTINGS
    cursor.execute("SELECT data FROM settings WHERE id = 1")
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT INTO settings (id, data) VALUES (1, ?)",
            (json.dumps(DEFAULT_SETTINGS, ensure_ascii=False),),
        )

    conn.commit()
    conn.close()


def get_settings() -> dict:
    """Retrieves current user settings dict from SQLite database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM settings WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row["data"])
    except Exception as e:
        logger.error("Error reading settings from DB: %s", e)
    return dict(DEFAULT_SETTINGS)


def update_settings(new_data: dict) -> dict:
    """Updates user settings fields in database and returns updated settings."""
    current = get_settings()
    for k in DEFAULT_SETTINGS.keys():
        if k in new_data:
            current[k] = new_data[k]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE settings SET data = ? WHERE id = 1",
            (json.dumps(current, ensure_ascii=False),),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Error updating settings in DB: %s", e)
    return current


def reset_settings() -> dict:
    """Resets user settings back to DEFAULT_SETTINGS profile."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE settings SET data = ? WHERE id = 1",
            (json.dumps(DEFAULT_SETTINGS, ensure_ascii=False),),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Error resetting settings in DB: %s", e)
    return dict(DEFAULT_SETTINGS)


def log_chat(user_msg: str, category: str, resp_text: str):
    """Persists a chat message log entry into SQLite database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_message, category, response) VALUES (?, ?, ?)",
            (user_msg, category, resp_text),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Error logging chat to DB: %s", e)

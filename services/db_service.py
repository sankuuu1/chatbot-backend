import json
import sqlite3
import os
import logging

logger = logging.getLogger("bandhu.db")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bandhu_data.db")

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


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY DEFAULT 1,
            data TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            category TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
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

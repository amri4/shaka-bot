import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "shaka.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS judgments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                judge_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                verdict TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def add_judgment(guild_id, judge_id, target_id, reason, verdict):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO judgments (guild_id, judge_id, target_id, reason, verdict) VALUES (?, ?, ?, ?, ?)",
            (str(guild_id), str(judge_id), str(target_id), reason, verdict),
        )
        conn.commit()


def get_recent_judgments(guild_id, limit=5):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, judge_id, target_id, reason, verdict, timestamp FROM judgments WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
            (str(guild_id), limit),
        ).fetchall()
    return rows


def get_judgment_by_id(judgment_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, judge_id, target_id, reason, verdict, timestamp FROM judgments WHERE id = ?",
            (judgment_id,),
        ).fetchone()
    return row

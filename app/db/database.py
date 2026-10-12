"""
Database connection and execution manager supporting SQLite and PostgreSQL.
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_FILE = os.getenv("SQLITE_DB_PATH", "ssms.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")


def get_db_path() -> str:
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "")
    return DB_FILE


def get_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def execute_commit(query: str, params: tuple = ()) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def execute_script(script_text: str):
    conn = get_connection()
    try:
        conn.executescript(script_text)
        conn.commit()
    finally:
        conn.close()

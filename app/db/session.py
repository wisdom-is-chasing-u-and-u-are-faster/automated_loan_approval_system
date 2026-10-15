import sqlite3
import os
from contextlib import contextmanager
from app.core.config import settings

_db_initialized = False

def get_raw_connection():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
    if not db_path:
        db_path = "alas.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_initialized():
    global _db_initialized
    if not _db_initialized:
        _db_initialized = True
        try:
            from app.db.init_db import init_database
            init_database()
        except Exception as e:
            print(f"DB auto-init notice: {e}")

def get_db_connection():
    """Returns a raw SQLite connection with dictionary row factory for high performance."""
    ensure_initialized()
    return get_raw_connection()

@contextmanager
def get_db():
    """Context manager for database operations with automatic commit and error rollback."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

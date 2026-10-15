import os
import pytest
from app.db.init_db import init_database
from app.db.session import get_db

def test_database_initialization_and_seeds():
    """Validates that DDL schemas and DML baseline seeds execute without errors."""
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()["count"]
        assert user_count >= 4

        cursor.execute("SELECT COUNT(*) as count FROM loan_applications")
        app_count = cursor.fetchone()["count"]
        assert app_count >= 4

        cursor.execute("SELECT COUNT(*) as count FROM decision_history")
        hist_count = cursor.fetchone()["count"]
        assert hist_count >= 6

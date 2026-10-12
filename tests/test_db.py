"""
Tests for Database Schema, Initializer, and Connection Manager.
Maps to AC: [ARCH-2617-AC1] Users can log in according to their assigned role (Student, Faculty, Admin).
"""
import pytest
from app.db.database import execute_query, execute_one
from app.db.init_db import init_database


def test_database_initialization():
    """Verify database tables and baseline seeds are loaded correctly."""
    init_database()
    users = execute_query("SELECT * FROM users")
    assert len(users) >= 3

    roles = {u["role"] for u in users}
    assert "student" in roles
    assert "faculty" in roles
    assert "admin" in roles


def test_courses_and_sections_seeded():
    """Verify default courses and sections exist in database."""
    init_database()
    courses = execute_query("SELECT * FROM courses")
    assert len(courses) >= 3

    sections = execute_query("SELECT * FROM course_sections")
    assert len(sections) >= 3

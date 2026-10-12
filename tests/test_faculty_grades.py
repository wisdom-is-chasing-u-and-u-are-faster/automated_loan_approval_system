"""
Tests for Faculty Course Views and Bulk Grade Submission.
Maps to AC: [ARCH-2617-AC3] Faculty can view their assigned courses and submit grades for enrolled students.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_faculty_view_assigned_courses():
    """Verify faculty can view list of assigned teaching courses."""
    res = client.get("/api/v1/faculty/courses")
    assert res.status_code == 200
    data = res.json()
    assert "assigned_courses" in data
    assert len(data["assigned_courses"]) > 0


def test_faculty_view_gradebook_roster():
    """Verify faculty can retrieve student gradebook roster for course."""
    res = client.get("/api/v1/faculty/courses/crs-101/gradebook")
    assert res.status_code == 200
    data = res.json()
    assert "students" in data


def test_faculty_bulk_grade_submission():
    """Verify faculty can perform bulk grade submission for enrolled students."""
    payload = {
        "course_id": "crs-101",
        "grades": [
            {
                "student_id": "stu-001",
                "letter_grade": "A",
                "score": 95.0
            }
        ]
    }
    res = client.post("/api/v1/faculty/grades/bulk-submit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["processed_records"] >= 1

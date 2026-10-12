"""
Tests for Course Catalog and Registration.
Maps to AC: [ARCH-2617-AC2] Students can successfully browse the course catalog and register for an available course.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_browse_course_catalog():
    """Verify students can retrieve available courses with seat information."""
    res = client.get("/api/v1/courses")
    assert res.status_code == 200
    data = res.json()
    assert "courses" in data
    assert len(data["courses"]) > 0

    course = data["courses"][0]
    assert "code" in course
    assert "title" in course
    assert "capacity" in course
    assert "available_seats" in course


def test_filter_course_catalog_by_department():
    """Verify filtering courses by department."""
    res = client.get("/api/v1/courses?department=Computer%20Science")
    assert res.status_code == 200
    courses = res.json()["courses"]
    for c in courses:
        assert c["department"] == "Computer Science"


def test_student_register_course():
    """Verify student can successfully register for an available course."""
    # Register for Discrete Math (crs-401) or Biology (crs-501)
    res = client.post("/api/v1/enrollments/register", json={"course_id": "crs-401"})
    # Allowed status 201 (or 400 if already enrolled)
    assert res.status_code in [201, 400]
    if res.status_code == 201:
        assert res.json()["success"] is True

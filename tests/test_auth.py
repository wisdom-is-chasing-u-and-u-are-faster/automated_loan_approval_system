"""
Tests for Authentication and Role-Based Access Control.
Maps to AC: [ARCH-2617-AC1] Users can log in according to their assigned role (Student, Faculty, Admin).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_student_login_success():
    """Verify Student login returns valid JWT token and student profile."""
    res = client.post("/api/v1/auth/login", json={
        "email": "student@university.edu",
        "password": "dev_test_password_123", # pragma: allowlist secret
        "role": "student"
    })
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "student"
    assert data["user"]["name"] == "Alex Rivers"
    assert data["user"]["student_id"] == "STU-2026-001"


def test_faculty_login_success():
    """Verify Faculty login returns valid JWT token and faculty profile."""
    res = client.post("/api/v1/auth/login", json={
        "email": "faculty@university.edu",
        "password": "dev_test_password_123", # pragma: allowlist secret
        "role": "faculty"
    })
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "faculty"
    assert data["user"]["department"] == "Computer Science"


def test_admin_login_success():
    """Verify Admin login returns valid JWT token and admin profile."""
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@university.edu",
        "password": "dev_test_password_123", # pragma: allowlist secret
        "role": "admin"
    })
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "admin"


def test_get_me_profile():
    """Verify GET /api/v1/auth/me returns current user profile."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "student@university.edu",
        "password": "dev_test_password_123" # pragma: allowlist secret
    })
    token = login_res.json()["token"]

    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "student@university.edu"

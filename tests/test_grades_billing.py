"""
Tests for Student Grade Viewing, GPA Calculation, and Tuition Billing.
Maps to AC: [ARCH-2617-AC4] Students can view their grades and tuition bills.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_student_view_my_grades():
    """Verify students can view current grades and cumulative GPA."""
    res = client.get("/api/v1/grades/my-grades")
    assert res.status_code == 200
    data = res.json()
    assert "cumulative_gpa" in data
    assert "semesters" in data


def test_student_view_tuition_invoices():
    """Verify students can view tuition bills and itemized fee breakdown."""
    res = client.get("/api/v1/billing/invoices")
    assert res.status_code == 200
    data = res.json()
    assert "total_balance_due" in data
    assert "invoices" in data
    assert len(data["invoices"]) > 0

    inv = data["invoices"][0]
    assert "amount" in inv
    assert "status" in inv
    assert "line_items" in inv

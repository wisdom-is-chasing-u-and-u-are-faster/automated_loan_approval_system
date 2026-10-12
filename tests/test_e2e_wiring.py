"""
Tests for Full-Stack E2E Static Mounting and Cross-Tier Wiring.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_probe():
    """Verify container orchestrator health probe returns 200 OK."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_public_index_serving():
    """Verify root / serves main landing HTML page."""
    res = client.get("/")
    assert res.status_code == 200
    assert "html" in res.headers.get("content-type", "").lower() or "text" in res.headers.get("content-type", "").lower()


def test_public_pages_serving():
    """Verify UI subpages are mounted and reachable."""
    pages = [
        "/pages/login.html",
        "/pages/student-dashboard.html",
        "/pages/course-registration.html",
        "/pages/my-grades.html",
        "/pages/tuition-billing.html",
        "/pages/transcript-request.html",
        "/pages/faculty-my-courses.html",
        "/pages/faculty-gradebook.html",
        "/pages/admin-dashboard.html",
        "/pages/admin-course-management.html"
    ]
    for page in pages:
        res = client.get(page)
        assert res.status_code == 200, f"Failed serving {page}"


def test_client_api_js_serving():
    """Verify JavaScript client API layer is mounted."""
    res = client.get("/js/api.js")
    assert res.status_code == 200
    assert "SSMS_API" in res.text


def test_admin_dashboard_and_audit_logs():
    """Verify Admin dashboard metrics and FERPA compliance audit inspector."""
    res_dash = client.get("/api/v1/admin/dashboard")
    assert res_dash.status_code == 200
    assert "metrics" in res_dash.json()

    res_audit = client.get("/api/v1/admin/audit-logs")
    assert res_audit.status_code == 200
    assert "logs" in res_audit.json()

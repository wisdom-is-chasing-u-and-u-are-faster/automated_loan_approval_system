import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_metrics():
    """Validates real-time dashboard metrics endpoint."""
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["applications_today"] >= 1000
    assert data["approval_rate_pct"] > 50.0
    assert data["manual_review_count"] >= 1
    assert data["avg_decision_time_sec"] < 1.0

def test_volume_history():
    """Validates 30-day volume history query."""
    response = client.get("/api/v1/dashboard/volume-history")
    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) >= 2

def test_reporting_endpoint():
    """Validates compliance reporting and analytics endpoint."""
    response = client.get("/api/v1/reports?report_type=daily_summary&start_date=2024-07-01&end_date=2024-07-21")
    assert response.status_code == 200
    data = response.json()
    assert data["report_type"] == "daily_summary"
    assert len(data["summary"]) >= 2

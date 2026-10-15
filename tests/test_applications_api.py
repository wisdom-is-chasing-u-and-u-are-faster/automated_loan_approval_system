import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_applications():
    """Validates query of loan applications queue."""
    response = client.get("/api/v1/applications")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert len(data["applications"]) >= 4

def test_list_applications_filter_by_status():
    """Validates filtering loan applications by status."""
    response = client.get("/api/v1/applications?status=APPROVED")
    assert response.status_code == 200
    data = response.json()
    for app in data["applications"]:
        assert app["status"] == "APPROVED"

def test_submit_auto_approved_loan_application():
    """Validates prime applicant triggers sub-second automated approval."""
    payload = {
        "applicant_name": "Bruce Wayne",
        "dob": "1980-02-19",
        "email": "bruce@waynecorp.com",
        "phone": "+1 (555) 777-8888",
        "address": "1007 Mountain Drive, Gotham City, USA",
        "loan_type": "Mortgage",
        "amount_requested": 500000.0,
        "loan_term_months": 360,
        "credit_score": 820,
        "annual_income": 500000.0,
        "debt_to_income_ratio": 15.0,
        "employer_name": "Wayne Enterprises"
    }
    response = client.post("/api/v1/applications", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "APPROVED"
    assert "instant approval" in data["decision_notes"].lower()
    assert data["decision_time_ms"] < 1000.0  # sub-second decisioning

def test_submit_manual_review_loan_application():
    """Validates middle-tier applicant is flagged for manual review."""
    payload = {
        "applicant_name": "Peter Parker",
        "dob": "1995-08-10",
        "email": "peter@dailybugle.com",
        "phone": "+1 (555) 123-9999",
        "address": "20 Ingram St, Queens, NY",
        "loan_type": "Personal",
        "amount_requested": 5000.0,
        "loan_term_months": 24,
        "credit_score": 670,
        "annual_income": 45000.0,
        "debt_to_income_ratio": 38.0,
        "employer_name": "Daily Bugle"
    }
    response = client.post("/api/v1/applications", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "MANUAL_REVIEW"
    assert "manual review" in data["decision_notes"].lower()

def test_get_application_details():
    """Validates retrieval of detailed application profile, loan terms, and decision audit logs."""
    response = client.get("/api/v1/applications/APP-2024-0815")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "APP-2024-0815"
    assert data["applicant"]["name"] == "John Doe"
    assert data["loan_details"]["credit_score"] == 680
    assert len(data["decision_history"]) >= 2

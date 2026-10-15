import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    """Validates login issues a valid JWT access token and user profile."""
    response = client.post("/api/v1/auth/login", json={
        "email": "alice.a@alas.com",
        "password": "TestAuthPass123!"  # pragma: whitelist secret
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "Administrator"

def test_login_invalid_credentials():
    """Validates login rejects invalid credentials with 401 Unauthorized."""
    response = client.post("/api/v1/auth/login", json={
        "email": "unknown@alas.com",
        "password": "InvalidAuthPass123!"  # pragma: whitelist secret
    })
    assert response.status_code == 401

def test_user_me_profile_and_permissions():
    """Validates /auth/me returns identity and RBAC permissions."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "alice.a@alas.com",
        "password": "TestAuthPass123!"  # pragma: whitelist secret
    })
    token = login_res.json()["access_token"]
    
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "Administrator"
    assert "write:all" in data["permissions"]

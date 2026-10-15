import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_users():
    """Validates user listing."""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert len(data["users"]) >= 4

def test_create_and_update_user():
    """Validates creating and updating user RBAC roles."""
    unique_email = f"test.underwriter.{int(time.time() * 1000)}@alas.com"
    create_payload = {
        "full_name": "Test Underwriter",
        "email": unique_email,
        "password": "TestAuthPass123!",  # pragma: whitelist secret
        "role": "Reviewer"
    }
    create_res = client.post("/api/v1/users", json=create_payload)
    assert create_res.status_code == 201
    user_data = create_res.json()
    assert user_data["email"] == unique_email
    user_id = user_data["user_id"]

    # Update role to Administrator
    update_res = client.put(f"/api/v1/users/{user_id}", json={"role": "Administrator"})
    assert update_res.status_code == 200
    assert update_res.json()["role"] == "Administrator"

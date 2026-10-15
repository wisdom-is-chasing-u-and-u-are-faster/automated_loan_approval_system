from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_probe():
    """Validates /health readiness probe returns 200 OK and valid payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Enterprise Automatic Loan Approval System" in data["service"]
    assert "version" in data
    assert "timestamp" in data

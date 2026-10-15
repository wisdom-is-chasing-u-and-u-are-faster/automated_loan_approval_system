import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_static_html_screens_and_assets():
    """Validates that all UI pages and static assets return 200 OK."""
    screens = [
        "/",
        "/index.html",
        "/dashboard.html",
        "/applications-queue.html",
        "/application-details.html",
        "/manual-review.html",
        "/reporting.html",
        "/user-management.html",
        "/css/styles.css",
        "/js/api.js"
    ]
    for screen in screens:
        res = client.get(screen)
        assert res.status_code == 200, f"Expected 200 for {screen}, got {res.status_code}"

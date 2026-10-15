import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_manual_review_queue_and_adjudication():
    """Validates manual review queue retrieval and underwriter adjudication workflow."""
    # 1. Fetch manual review queue
    res_queue = client.get("/api/v1/applications/queue/manual-review")
    assert res_queue.status_code == 200
    queue_data = res_queue.json()
    assert queue_data["total"] >= 1
    
    app_id = queue_data["applications"][0]["id"]

    # 2. Adjudicate application (Approve with notes)
    adj_payload = {
        "action": "APPROVE",
        "review_notes": "Automated test underwriter approval: Applicant verified."
    }
    res_adj = client.post(f"/api/v1/applications/{app_id}/adjudicate", json=adj_payload)
    assert res_adj.status_code == 200
    adj_data = res_adj.json()
    assert adj_data["id"] == app_id
    assert adj_data["status"] == "APPROVED"

    # 3. Verify status updated and recorded in decision history
    res_detail = client.get(f"/api/v1/applications/{app_id}")
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["status"] == "APPROVED"
    assert any(h["stage"] == "Manual Adjudication" for h in detail_data["decision_history"])

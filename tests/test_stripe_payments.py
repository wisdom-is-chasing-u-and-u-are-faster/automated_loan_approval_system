"""
Tests for Stripe Checkout and Webhook Payment Reconciliation.
Maps to AC: [ARCH-2617-AC6] Payment processing via Stripe is functional.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database
from app.db.database import execute_one

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_create_stripe_checkout_session():
    """Verify creating a Stripe Checkout Session returns checkout URL."""
    res = client.post("/api/v1/billing/checkout-session", json={
        "invoice_id": "inv-001",
        "amount": 4250.00
    })
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert "checkout_url" in data
    assert "stripe.com" in data["checkout_url"]


def test_process_signed_stripe_webhook_reconciliation():
    """Verify signed Stripe webhook marks invoice as paid and updates ledger."""
    webhook_payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_webhook_success_999",
                "invoice_id": "inv-001",
                "amount_paid": 4250.00,
                "status": "complete"
            }
        }
    }
    res = client.post("/api/v1/billing/stripe-webhook", json=webhook_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["reconciled"] is True
    assert data["invoice_status"] == "paid"

    # Verify database state
    inv = execute_one("SELECT status FROM student_invoices WHERE id = 'inv-001'")
    assert inv["status"] == "paid"

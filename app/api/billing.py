"""
Tuition Billing & Stripe Integration API Router.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.db.database import execute_query, execute_one
from app.models.billing import CheckoutSessionRequest, CheckoutSessionResponse, WebhookPayload
from app.services.stripe_service import create_stripe_checkout_session, reconcile_stripe_webhook
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.get("/invoices")
def get_invoices(user: dict = Depends(get_current_user)):
    student = execute_one("SELECT id FROM students WHERE user_id = ? OR id = ?", (user["id"], user["id"]))
    student_id = student["id"] if student else "stu-001"

    invoices = execute_query(
        "SELECT * FROM student_invoices WHERE student_id = ? ORDER BY created_at DESC",
        (student_id,)
    )

    enriched_invoices = []
    total_balance = 0.0

    for inv in invoices:
        items = execute_query("SELECT description, amount FROM invoice_items WHERE invoice_id = ?", (inv["id"],))
        inv_dict = dict(inv)
        inv_dict["line_items"] = items
        enriched_invoices.append(inv_dict)
        if inv["status"] == "unpaid":
            total_balance += float(inv["amount"])

    payments = execute_query(
        """
        SELECT p.id as payment_id, p.created_at as date, p.amount, p.payment_method as method, p.status
        FROM payment_records p
        JOIN student_invoices si ON p.invoice_id = si.id
        WHERE si.student_id = ?
        ORDER BY p.created_at DESC
        """,
        (student_id,)
    )

    return {
        "student_id": student_id,
        "total_balance_due": total_balance,
        "invoices": enriched_invoices,
        "payment_history": payments
    }


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(req: CheckoutSessionRequest, user: dict = Depends(get_current_user)):
    result = create_stripe_checkout_session(req.invoice_id, req.amount, req.currency or "usd")
    if not result.get("session_id"):
        raise HTTPException(status_code=400, detail="Unable to create checkout session")
    return CheckoutSessionResponse(**result)


@router.post("/stripe-webhook")
def stripe_webhook(payload: WebhookPayload):
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    result = reconcile_stripe_webhook(data)
    return result

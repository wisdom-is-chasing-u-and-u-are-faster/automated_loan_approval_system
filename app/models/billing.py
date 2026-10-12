from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class CheckoutSessionRequest(BaseModel):
    invoice_id: str
    amount: float
    currency: Optional[str] = "usd"


class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str


class WebhookPayload(BaseModel):
    type: str
    data: Dict[str, Any]

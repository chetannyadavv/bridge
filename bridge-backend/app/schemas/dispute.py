from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.dispute import DisputeStatus


class DisputeCreate(BaseModel):
    transaction_id: str
    merchant_name: str
    amount: Decimal
    currency: str = "USD"
    reason: str
    # Sprint 5: optional explicit AMEX reason code. If omitted, the
    # backend infers it from `reason`'s free text (see
    # app.decision_engine.reason_codes.infer_reason_code) — the frontend
    # doesn't need to change to keep working.
    reason_code: str | None = None


class DisputeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    transaction_id: str
    customer_name: str
    merchant_name: str
    reason: str
    reason_code: str | None = None
    amount: Decimal
    currency: str
    status: DisputeStatus
    created_at: datetime

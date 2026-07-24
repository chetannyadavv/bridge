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


class DisputeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    transaction_id: str
    customer_name: str
    merchant_name: str
    reason: str
    amount: Decimal
    currency: str
    status: DisputeStatus
    created_at: datetime

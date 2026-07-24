from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.recommendation import RecommendationType


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dispute_id: str
    recommendation: RecommendationType
    percentage: int | None
    reason: str
    explanation: str
    accepted_by: list[str]
    updated_at: datetime


class AcceptRecommendationRequest(BaseModel):
    role: str  # "cardholder" | "merchant" — no auth yet, caller states its own role

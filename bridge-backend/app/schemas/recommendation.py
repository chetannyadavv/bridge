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

    # Sprint 5 additions — full Decision Engine output. Nullable/empty on
    # any recommendation row created before this sprint.
    reason_code: str | None = None
    category: str | None = None
    engine_recommendation: str | None = None
    confidence: int | None = None
    summary: str | None = None
    reasons: list[str] = []
    missing_evidence: list[str] = []
    next_steps: list[str] = []


class AcceptRecommendationRequest(BaseModel):
    role: str  # "cardholder" | "merchant" — no auth yet, caller states its own role

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.dispute import Dispute, DisputeStatus
from app.models.evidence import Evidence, CredibilityLabel
from app.models.recommendation import Recommendation, RecommendationType
from app.models.timeline_event import TimelineEvent

# Sprint 3: mock-only recommendation logic, deliberately simple — ported
# 1:1 from the frontend's Sprint 2 settlementService.ts so behavior is
# unchanged now that the backend is the source of truth.
#
# Sprint 5 note: this file is the seam. `compute_recommendation` is the
# only place a recommendation is computed — swap its body for a real
# call (LLM / rules engine) without changing its signature or callers.

CORROBORATING_LABELS = {
    CredibilityLabel.VERIFIED_TRANSACTION,
    CredibilityLabel.GPS_CONFIRMED,
    CredibilityLabel.TIMESTAMPED_RECEIPT,
}


def compute_recommendation(
    dispute_id: str, evidence_items: list[Evidence], previous: Recommendation | None
) -> Recommendation:
    corroborating_count = sum(1 for e in evidence_items if e.credibility in CORROBORATING_LABELS)
    has_merchant = any(e.uploader.value == "merchant" for e in evidence_items)
    has_cardholder = any(e.uploader.value == "cardholder" for e in evidence_items)

    recommendation = RecommendationType.NO_REFUND
    percentage = 0
    reason = "Not enough corroborating evidence has been submitted yet."
    explanation = "Once more evidence is available, this recommendation will update automatically."

    if has_merchant and has_cardholder and corroborating_count >= 2:
        recommendation = RecommendationType.PARTIAL_REFUND
        percentage = 50
        reason = "Evidence from both parties partially corroborates the claim."
        explanation = (
            f"Based on the evidence submitted so far, a {percentage}% refund reflects a claim "
            "that is partially, but not fully, supported by verified evidence."
        )
    elif has_cardholder and corroborating_count >= 1:
        recommendation = RecommendationType.PARTIAL_REFUND
        percentage = 50
        reason = "Cardholder evidence is corroborated by a verified record; awaiting merchant response."
        explanation = (
            "The cardholder's claim is supported by at least one verified record. This "
            "recommendation may change once the merchant responds."
        )

    return Recommendation(
        id=f"st_{uuid.uuid4().hex[:10]}",
        dispute_id=dispute_id,
        recommendation=recommendation,
        percentage=percentage,
        reason=reason,
        explanation=explanation,
        accepted_by=list(previous.accepted_by) if previous else [],
    )


def list_recommendations(db: Session, dispute_id: str) -> list[Recommendation]:
    return (
        db.query(Recommendation)
        .filter(Recommendation.dispute_id == dispute_id)
        .order_by(Recommendation.updated_at)
        .all()
    )


def get_latest_recommendation(db: Session, dispute_id: str) -> Recommendation | None:
    return (
        db.query(Recommendation)
        .filter(Recommendation.dispute_id == dispute_id)
        .order_by(Recommendation.updated_at.desc())
        .first()
    )


def accept_recommendation(db: Session, dispute: Dispute, role: str) -> Recommendation | None:
    latest = get_latest_recommendation(db, dispute.id)
    if latest is None:
        return None

    accepted = list(latest.accepted_by or [])
    if role not in accepted:
        accepted.append(role)
    latest.accepted_by = accepted
    dispute.status = DisputeStatus.RESOLVED

    db.add(
        TimelineEvent(
            id=f"evt_{uuid.uuid4().hex[:10]}",
            dispute_id=dispute.id,
            timestamp=datetime.now(timezone.utc),
            title="Dispute Resolved",
            description=f"{'Cardholder' if role == 'cardholder' else 'Merchant'} accepted the settlement recommendation.",
        )
    )

    db.commit()
    db.refresh(latest)
    return latest

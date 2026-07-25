import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.dispute import Dispute, DisputeStatus
from app.models.evidence import Evidence
from app.models.recommendation import Recommendation, RecommendationType
from app.models.timeline_event import TimelineEvent

from app.decision_engine import DecisionEngine
from app.decision_engine.recommendation_formatter import format_recommendation
from app.decision_engine.decision_engine import Recommendation as EngineRecommendation

_ENGINE_TO_LEGACY: dict[EngineRecommendation, tuple[RecommendationType, int]] = {
    EngineRecommendation.APPROVE_REFUND: (RecommendationType.FULL_REFUND, 100),
    EngineRecommendation.REJECT_REFUND: (RecommendationType.NO_REFUND, 0),
    EngineRecommendation.PARTIAL_REFUND: (RecommendationType.PARTIAL_REFUND, 50),
    EngineRecommendation.REQUEST_ADDITIONAL_EVIDENCE: (RecommendationType.NO_REFUND, 0),
    EngineRecommendation.ESCALATE_FOR_MANUAL_REVIEW: (RecommendationType.NO_REFUND, 0),
}

# Bug fix: a dispute must not be marked RESOLVED until BOTH parties have
# accepted. Previously this function set dispute.status = RESOLVED on
# ANY single acceptance, which meant the moment either party clicked
# Accept, the OTHER party's screen also read dispute.status === RESOLVED
# and rendered the final "Dispute resolved" outcome — even though they
# themselves had never agreed to anything.
REQUIRED_ACCEPTANCE_ROLES = {"cardholder", "merchant"}


def compute_recommendation(
    dispute: Dispute, evidence_items: list[Evidence], previous: Recommendation | None
) -> Recommendation:
    engine = DecisionEngine()
    result = engine.compute(dispute, evidence_items)
    formatted = format_recommendation(result)

    legacy_type, legacy_percentage = _ENGINE_TO_LEGACY[result.recommendation]

    accepted = list(previous.accepted_by) if previous else []

    return Recommendation(
        id=f"st_{uuid.uuid4().hex[:10]}",
        dispute_id=dispute.id,
        recommendation=legacy_type,
        percentage=legacy_percentage,
        reason=formatted.summary,
        explanation=formatted.summary,
        accepted_by=accepted,
        sequence=(previous.sequence + 1) if previous else 0,
        reason_code=result.reason_code,
        category=result.category,
        engine_recommendation=result.recommendation.value,
        confidence=result.confidence,
        summary=formatted.summary,
        reasons=formatted.reasons,
        missing_evidence=formatted.missing_evidence,
        next_steps=formatted.next_steps,
    )


def list_recommendations(db: Session, dispute_id: str) -> list[Recommendation]:
    return (
        db.query(Recommendation)
        .filter(Recommendation.dispute_id == dispute_id)
        .order_by(Recommendation.sequence)
        .all()
    )


def get_latest_recommendation(db: Session, dispute_id: str) -> Recommendation | None:
    return (
        db.query(Recommendation)
        .filter(Recommendation.dispute_id == dispute_id)
        .order_by(Recommendation.sequence.desc())
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

    role_label = "Cardholder" if role == "cardholder" else "Merchant"
    fully_accepted = REQUIRED_ACCEPTANCE_ROLES.issubset(set(accepted))

    if fully_accepted:
        dispute.status = DisputeStatus.RESOLVED
        db.add(
            TimelineEvent(
                id=f"evt_{uuid.uuid4().hex[:10]}",
                dispute_id=dispute.id,
                timestamp=datetime.now(timezone.utc),
                title="Dispute Resolved",
                description=f"{role_label} accepted the settlement recommendation. "
                            "Both parties have now accepted — dispute resolved.",
            )
        )
    else:
        db.add(
            TimelineEvent(
                id=f"evt_{uuid.uuid4().hex[:10]}",
                dispute_id=dispute.id,
                timestamp=datetime.now(timezone.utc),
                title="Settlement Accepted",
                description=f"{role_label} accepted the settlement recommendation. "
                            "Awaiting acceptance from the other party.",
            )
        )

    db.commit()
    db.refresh(latest)
    return latest

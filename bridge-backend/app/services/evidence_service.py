import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.dispute import Dispute, DisputeStatus
from app.models.evidence import Evidence
from app.models.timeline_event import TimelineEvent
from app.schemas.evidence import EvidenceCreate
from app.services.recommendation_service import compute_recommendation, get_latest_recommendation


def list_evidence(db: Session, dispute_id: str) -> list[Evidence]:
    return (
        db.query(Evidence)
        .filter(Evidence.dispute_id == dispute_id)
        .order_by(Evidence.created_at)
        .all()
    )


def add_evidence(db: Session, dispute: Dispute, payload: EvidenceCreate) -> Evidence:
    evidence = Evidence(
        id=f"ev_{uuid.uuid4().hex[:10]}",
        dispute_id=dispute.id,
        uploader=payload.uploader,
        type=payload.type,
        credibility=payload.credibility,
        summary=payload.summary,
        file_path=payload.file_path,
    )
    db.add(evidence)
    db.flush()  # populate evidence.created_at before it's used below

    title = "Merchant Response Added" if payload.uploader.value == "merchant" else "Evidence Uploaded"
    db.add(
        TimelineEvent(
            id=f"evt_{uuid.uuid4().hex[:10]}",
            dispute_id=dispute.id,
            timestamp=evidence.created_at or datetime.now(timezone.utc),
            title=title,
            description=evidence.summary,
        )
    )

    if dispute.status == DisputeStatus.OPEN:
        dispute.status = DisputeStatus.IN_NEGOTIATION

    # Flushed evidence is visible to a fresh query within the same
    # transaction, so this already includes the row just added above.
    all_evidence = list_evidence(db, dispute.id)
    previous_recommendation = get_latest_recommendation(db, dispute.id)
    recommendation = compute_recommendation(dispute.id, all_evidence, previous_recommendation)
    db.add(recommendation)
    db.flush()

    # Only announce a fresh "recommendation ready" moment the first time a
    # recommendation exists for this dispute, so the timeline doesn't get a
    # duplicate entry on every subsequent evidence submission.
    if previous_recommendation is None:
        db.add(
            TimelineEvent(
                id=f"evt_{uuid.uuid4().hex[:10]}",
                dispute_id=dispute.id,
                timestamp=recommendation.updated_at or datetime.now(timezone.utc),
                title="Recommendation Pending",
                description="A settlement recommendation is now available for review.",
            )
        )

    db.commit()
    db.refresh(evidence)
    return evidence

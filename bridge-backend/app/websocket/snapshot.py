from sqlalchemy.orm import Session

from app.schemas.dispute import DisputeOut
from app.schemas.evidence import EvidenceOut
from app.schemas.timeline_event import TimelineEventOut
from app.schemas.recommendation import RecommendationOut
from app.services import dispute_service, evidence_service, timeline_service, recommendation_service


def build_dispute_snapshot_messages(db: Session, dispute_id: str) -> list[dict]:
    """
    Builds the four messages representing a dispute's full mutable state
    (dispute status, evidence, timeline, recommendations).

    Used in two places: when a client first connects (or reconnects) to
    /ws/disputes/{id} — so it catches up immediately with no separate
    REST call needed — and after any mutating REST call, to broadcast the
    new state to everyone else already in the room.

    Deliberately sends full snapshots rather than diffs: it sidesteps
    ordering/duplication bugs under concurrent writes entirely (the
    client always replaces its local state with what the server says is
    current), at the cost of a slightly larger payload — an easy trade
    at this scale, and simpler than reasoning about partial updates.
    """
    dispute = dispute_service.get_dispute(db, dispute_id)
    evidence_items = evidence_service.list_evidence(db, dispute_id)
    timeline_items = timeline_service.list_timeline(db, dispute_id)
    recommendation_items = recommendation_service.list_recommendations(db, dispute_id)

    return [
        {
            "type": "dispute_updated",
            "payload": DisputeOut.model_validate(dispute).model_dump(mode="json"),
        },
        {
            "type": "evidence_updated",
            "payload": [EvidenceOut.model_validate(e).model_dump(mode="json") for e in evidence_items],
        },
        {
            "type": "timeline_updated",
            "payload": [TimelineEventOut.model_validate(t).model_dump(mode="json") for t in timeline_items],
        },
        {
            "type": "recommendation_updated",
            "payload": [
                RecommendationOut.model_validate(r).model_dump(mode="json") for r in recommendation_items
            ],
        },
    ]

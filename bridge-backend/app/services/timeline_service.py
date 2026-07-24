from sqlalchemy.orm import Session

from app.models.timeline_event import TimelineEvent


def list_timeline(db: Session, dispute_id: str) -> list[TimelineEvent]:
    return (
        db.query(TimelineEvent)
        .filter(TimelineEvent.dispute_id == dispute_id)
        .order_by(TimelineEvent.timestamp)
        .all()
    )

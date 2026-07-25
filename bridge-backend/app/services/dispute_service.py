import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.dispute import Dispute, DisputeStatus
from app.models.transaction import Transaction
from app.models.timeline_event import TimelineEvent
from app.schemas.dispute import DisputeCreate
from app.decision_engine.reason_codes import infer_reason_code

# No authentication in this sprint — every dispute is filed by the same
# demo cardholder persona, matching the frontend's mock customer from
# earlier sprints so the UX doesn't change.
DEMO_CUSTOMER_NAME = "Priya Nair"


def list_disputes(db: Session) -> list[Dispute]:
    return db.query(Dispute).order_by(Dispute.created_at.desc()).all()


def get_dispute(db: Session, dispute_id: str) -> Dispute | None:
    return db.query(Dispute).filter(Dispute.id == dispute_id).first()


def create_dispute(db: Session, payload: DisputeCreate) -> Dispute:
    transaction = db.query(Transaction).filter(Transaction.id == payload.transaction_id).first()
    if transaction is None:
        transaction = Transaction(
            id=payload.transaction_id,
            merchant_name=payload.merchant_name,
            amount=payload.amount,
            currency=payload.currency,
            occurred_at=datetime.now(timezone.utc),
        )
        db.add(transaction)

    dispute = Dispute(
        id=f"dsp_{uuid.uuid4().hex[:10]}",
        transaction_id=payload.transaction_id,
        customer_name=DEMO_CUSTOMER_NAME,
        merchant_name=payload.merchant_name,
        reason=payload.reason,
        reason_code=payload.reason_code or infer_reason_code(payload.reason),
        amount=payload.amount,
        currency=payload.currency,
        status=DisputeStatus.OPEN,
    )
    db.add(dispute)
    db.flush()  # populate dispute.created_at (server_default) before using it below

    db.add(
        TimelineEvent(
            id=f"evt_{uuid.uuid4().hex[:10]}",
            dispute_id=dispute.id,
            timestamp=dispute.created_at or datetime.now(timezone.utc),
            title="Dispute Created",
            description=f"Cardholder opened a dispute: {payload.reason}.",
        )
    )

    db.commit()
    db.refresh(dispute)
    return dispute

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.dispute import Dispute, DisputeStatus
from app.models.evidence import Evidence, UploaderRole, EvidenceType, CredibilityLabel
from app.models.timeline_event import TimelineEvent
from app.models.recommendation import Recommendation, RecommendationType

# Fixed id — the frontend's Landing page links directly to
# /disputes/dsp_8841 ("View a live workspace"), so this id must stay
# stable across restarts for that link to keep working.
SEED_DISPUTE_ID = "dsp_8841"


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def seed_if_empty(db: Session) -> None:
    if db.query(Dispute).first() is not None:
        return  # already seeded — nothing to do

    txn = Transaction(
        id="txn_55291",
        merchant_name="Harborline Stays",
        amount=Decimal("340.00"),
        currency="USD",
        occurred_at=datetime(2026, 7, 12, 10, 3, tzinfo=timezone.utc),
    )
    db.add(txn)

    dispute = Dispute(
        id=SEED_DISPUTE_ID,
        transaction_id=txn.id,
        customer_name="Priya Nair",
        merchant_name="Harborline Stays",
        reason="Item not as described",
        amount=Decimal("340.00"),
        currency="USD",
        status=DisputeStatus.IN_NEGOTIATION,
        created_at=datetime(2026, 7, 18, 14, 12, tzinfo=timezone.utc),
    )
    db.add(dispute)

    for title, description, ts in [
        ("Booking confirmed", "Reservation made for a 2-night stay, Deluxe Harbor View room.",
         datetime(2026, 7, 12, 10, 2, tzinfo=timezone.utc)),
        ("Payment captured", "$340.00 charged to card ending 4471.",
         datetime(2026, 7, 12, 10, 3, tzinfo=timezone.utc)),
        ("Check-in recorded", "Guest checked in at property front desk.",
         datetime(2026, 7, 16, 15, 41, tzinfo=timezone.utc)),
        ("Guest message sent", "Guest messaged front desk: room did not match listing photos.",
         datetime(2026, 7, 16, 16, 20, tzinfo=timezone.utc)),
        ("Review posted", "Guest left a 2-star review citing room discrepancy.",
         datetime(2026, 7, 18, 9, 15, tzinfo=timezone.utc)),
        ("Dispute filed", "Cardholder opened a dispute: item not as described.",
         datetime(2026, 7, 18, 14, 12, tzinfo=timezone.utc)),
    ]:
        db.add(TimelineEvent(id=_uid("evt"), dispute_id=dispute.id, timestamp=ts, title=title, description=description))

    for uploader, etype, credibility, summary, ts in [
        (UploaderRole.system, EvidenceType.SYSTEM_RECORD, CredibilityLabel.VERIFIED_TRANSACTION,
         "Transaction record — $340.00 to Harborline Stays on Jul 12.",
         datetime(2026, 7, 18, 14, 12, 5, tzinfo=timezone.utc)),
        (UploaderRole.system, EvidenceType.SYSTEM_RECORD, CredibilityLabel.TIMESTAMPED_RECEIPT,
         "Booking confirmation — Deluxe Harbor View, 2 nights.",
         datetime(2026, 7, 18, 14, 12, 6, tzinfo=timezone.utc)),
        (UploaderRole.cardholder, EvidenceType.IMAGE, CredibilityLabel.CUSTOMER_STATEMENT,
         "Photo of the room actually provided at check-in.",
         datetime(2026, 7, 18, 14, 20, tzinfo=timezone.utc)),
        (UploaderRole.merchant, EvidenceType.SYSTEM_RECORD, CredibilityLabel.GPS_CONFIRMED,
         "Front-desk check-in log with device GPS confirmation.",
         datetime(2026, 7, 18, 15, 2, tzinfo=timezone.utc)),
        (UploaderRole.merchant, EvidenceType.TEXT, CredibilityLabel.MERCHANT_STATEMENT,
         "Merchant statement: guest was offered a room change, declined.",
         datetime(2026, 7, 18, 15, 5, tzinfo=timezone.utc)),
    ]:
        db.add(Evidence(id=_uid("ev"), dispute_id=dispute.id, uploader=uploader, type=etype,
                         credibility=credibility, summary=summary, created_at=ts))

    db.add(Recommendation(
        id=_uid("st"), dispute_id=dispute.id, recommendation=RecommendationType.NO_REFUND,
        percentage=0, reason="Insufficient corroborating evidence at time of filing.",
        explanation="Only the cardholder's statement was available when the dispute opened, so no "
                    "refund could be recommended yet.",
        accepted_by=[], updated_at=datetime(2026, 7, 18, 14, 13, tzinfo=timezone.utc),
    ))
    db.add(Recommendation(
        id=_uid("st"), dispute_id=dispute.id, recommendation=RecommendationType.PARTIAL_REFUND,
        percentage=50, reason="Room discrepancy corroborated by photo; check-in confirmed via GPS.",
        explanation="The guest's photo shows a room inconsistent with the listing, and the merchant's "
                    "GPS-confirmed check-in log verifies the stay occurred. A 50% refund reflects a "
                    "valid discrepancy alongside a completed stay.",
        accepted_by=[], updated_at=datetime(2026, 7, 18, 15, 6, tzinfo=timezone.utc),
    ))

    # A few more disputes so Analyst View isn't empty on first load.
    for d_id, txn_id, merchant, reason, amount, status, created in [
        ("dsp_8790", "txn_55110", "Harborline Stays", "Duplicate charge",
         Decimal("89.50"), DisputeStatus.RESOLVED, datetime(2026, 7, 10, 9, 3, tzinfo=timezone.utc)),
        ("dsp_8705", "txn_54932", "Northgate Electronics", "Item not received",
         Decimal("212.75"), DisputeStatus.OPEN, datetime(2026, 7, 21, 18, 47, tzinfo=timezone.utc)),
        ("dsp_8622", "txn_54810", "Harborline Stays", "Service not rendered",
         Decimal("150.00"), DisputeStatus.CLOSED, datetime(2026, 6, 30, 11, 22, tzinfo=timezone.utc)),
    ]:
        db.add(Transaction(id=txn_id, merchant_name=merchant, amount=amount, currency="USD", occurred_at=created))
        db.add(Dispute(id=d_id, transaction_id=txn_id, customer_name="Priya Nair", merchant_name=merchant,
                        reason=reason, amount=amount, currency="USD", status=status, created_at=created))

    db.commit()

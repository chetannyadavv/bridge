import enum

from sqlalchemy import Column, String, Numeric, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class DisputeStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_NEGOTIATION = "IN_NEGOTIATION"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(String, primary_key=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)

    # No auth in this sprint — customer_name / merchant_name are plain
    # denormalized fields rather than a separate parties/users table.
    customer_name = Column(String, nullable=False)
    merchant_name = Column(String, nullable=False)

    reason = Column(String, nullable=False)
    # Sprint 5: set at creation (see dispute_service.create_dispute) —
    # either passed explicitly or inferred from the free-text `reason`
    # via app.decision_engine.reason_codes.infer_reason_code. Nullable
    # since a dispute may be filed under a reason with no known mapping.
    reason_code = Column(String, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(DisputeStatus), nullable=False, default=DisputeStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", back_populates="disputes")
    evidence_items = relationship(
        "Evidence", back_populates="dispute", cascade="all, delete-orphan", order_by="Evidence.created_at"
    )
    timeline_events = relationship(
        "TimelineEvent", back_populates="dispute", cascade="all, delete-orphan", order_by="TimelineEvent.timestamp"
    )
    recommendations = relationship(
        "Recommendation", back_populates="dispute", cascade="all, delete-orphan", order_by="Recommendation.updated_at"
    )

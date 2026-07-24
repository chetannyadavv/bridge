import enum

from sqlalchemy import Column, String, Text, ForeignKey, Enum, Integer, DateTime, JSON, func
from sqlalchemy.orm import relationship

from app.database import Base


class RecommendationType(str, enum.Enum):
    FULL_REFUND = "FULL_REFUND"
    PARTIAL_REFUND = "PARTIAL_REFUND"
    NO_REFUND = "NO_REFUND"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True)
    dispute_id = Column(String, ForeignKey("disputes.id"), nullable=False)
    recommendation = Column(Enum(RecommendationType), nullable=False)
    percentage = Column(Integer, nullable=True)
    reason = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)

    # List of roles ("cardholder" / "merchant") that have accepted this
    # recommendation. JSON keeps this portable (works the same on
    # Postgres and SQLite) without reaching for a separate join table
    # for what is, at MVP scale, a 0-2 element list.
    accepted_by = Column(JSON, nullable=False, default=list)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    dispute = relationship("Dispute", back_populates="recommendations")

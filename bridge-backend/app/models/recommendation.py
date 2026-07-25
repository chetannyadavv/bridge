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

    # Bug fix: `updated_at` alone is not a safe ordering key for "which
    # recommendation is latest" — SQLite's CURRENT_TIMESTAMP has only
    # second-level granularity, so two recommendations created within
    # the same second get IDENTICAL updated_at values. `sequence` is a
    # strictly monotonic, per-dispute counter assigned in Python at
    # construction time, with no dependency on wall-clock precision.
    sequence = Column(Integer, nullable=False, default=0)

    # --- Sprint 5: full Decision Engine output -----------------------
    # Purely additive — every column above is unchanged. `recommendation`
    # and `percentage` still carry the legacy 3-way value the existing
    # frontend reads; these columns carry the engine's full 5-way
    # output and reasoning for anyone (e.g. GET /disputes/{id}/decision)
    # who wants it. Nullable/empty on any row from before this sprint.
    reason_code = Column(String, nullable=True)
    category = Column(String, nullable=True)
    engine_recommendation = Column(String, nullable=True)  # the spec's literal 5-way value, e.g. "Approve Refund"
    confidence = Column(Integer, nullable=True)  # 0-100
    summary = Column(Text, nullable=True)
    reasons = Column(JSON, nullable=False, default=list)
    missing_evidence = Column(JSON, nullable=False, default=list)
    next_steps = Column(JSON, nullable=False, default=list)

    dispute = relationship("Dispute", back_populates="recommendations")

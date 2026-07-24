from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(String, primary_key=True)
    dispute_id = Column(String, ForeignKey("disputes.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    dispute = relationship("Dispute", back_populates="timeline_events")

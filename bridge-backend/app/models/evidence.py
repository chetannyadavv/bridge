import enum

from sqlalchemy import Column, String, Text, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class UploaderRole(str, enum.Enum):
    cardholder = "cardholder"
    merchant = "merchant"
    system = "system"


class EvidenceType(str, enum.Enum):
    IMAGE = "IMAGE"
    PDF = "PDF"
    TEXT = "TEXT"
    SYSTEM_RECORD = "SYSTEM_RECORD"


class CredibilityLabel(str, enum.Enum):
    VERIFIED_TRANSACTION = "VERIFIED_TRANSACTION"
    GPS_CONFIRMED = "GPS_CONFIRMED"
    TIMESTAMPED_RECEIPT = "TIMESTAMPED_RECEIPT"
    CUSTOMER_STATEMENT = "CUSTOMER_STATEMENT"
    MERCHANT_STATEMENT = "MERCHANT_STATEMENT"
    UNVERIFIED = "UNVERIFIED"


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True)
    dispute_id = Column(String, ForeignKey("disputes.id"), nullable=False)
    uploader = Column(Enum(UploaderRole), nullable=False)
    type = Column(Enum(EvidenceType), nullable=False)
    credibility = Column(Enum(CredibilityLabel), nullable=False)
    summary = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    dispute = relationship("Dispute", back_populates="evidence_items")

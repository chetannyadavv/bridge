from sqlalchemy import Column, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    merchant_name = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    occurred_at = Column(DateTime(timezone=True), nullable=False)

    disputes = relationship("Dispute", back_populates="transaction")

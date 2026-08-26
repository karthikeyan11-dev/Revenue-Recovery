import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class FailureReason(str, enum.Enum):
    BANK_DECLINED = "BANK_DECLINED"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    EXPIRED_CARD = "EXPIRED_CARD"
    NETWORK_ERROR = "NETWORK_ERROR"
    USER_DROPOFF = "USER_DROPOFF"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"


class PaymentFailure(Base):
    __tablename__ = "payment_failures"

    id = Column(String(64), primary_key=True, index=True)
    transaction_id = Column(
        String(64), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    failure_reason = Column(
        Enum(FailureReason, name="failure_reason_enum"),
        nullable=False,
        index=True,
    )
    raw_error_code = Column(String(64), nullable=True)
    raw_error_message = Column(Text, nullable=True)
    raw_error_source = Column(String(64), nullable=True)
    raw_error_step = Column(String(64), nullable=True)
    raw_error_reason = Column(String(64), nullable=True)
    razorpay_payment_id = Column(String(64), nullable=True, index=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="payment_failures")
    revenue_leaks = relationship(
        "RevenueLeak", back_populates="payment_failure", cascade="all, delete-orphan"
    )

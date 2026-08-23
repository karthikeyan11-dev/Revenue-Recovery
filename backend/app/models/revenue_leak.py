import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class LeakType(str, enum.Enum):
    TRANSACTION_FAILURE = "TRANSACTION_FAILURE"
    SUBSCRIPTION_LAPSE = "SUBSCRIPTION_LAPSE"
    CHECKOUT_ABANDONMENT = "CHECKOUT_ABANDONMENT"
    RECURRING_INVOICE_OVERDUE = "RECURRING_INVOICE_OVERDUE"


class RevenueLeak(Base):
    __tablename__ = "revenue_leaks"

    id = Column(String(64), primary_key=True, index=True)
    failure_id = Column(
        String(64),
        ForeignKey("payment_failures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    leak_type = Column(
        Enum(LeakType, name="leak_type_enum"),
        default=LeakType.TRANSACTION_FAILURE,
        nullable=False,
        index=True,
    )
    amount = Column(Float, nullable=False)
    confidence = Column(Float, default=0.9, nullable=False)
    recoverability_score = Column(Float, default=0.75, nullable=False)
    reasoning = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    payment_failure = relationship("PaymentFailure", back_populates="revenue_leaks")
    recovery_case = relationship(
        "RecoveryCase", back_populates="revenue_leak", uselist=False, cascade="all, delete-orphan"
    )

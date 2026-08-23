import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db import Base


class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class PaymentMethod(str, enum.Enum):
    CARD = "CARD"
    UPI = "UPI"
    NETBANKING = "NETBANKING"
    WALLET = "WALLET"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(64), primary_key=True, index=True)
    customer_id = Column(
        String(64), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="INR", nullable=False)
    status = Column(
        Enum(TransactionStatus, name="transaction_status_enum"),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True,
    )
    payment_method = Column(
        Enum(PaymentMethod, name="payment_method_enum"),
        default=PaymentMethod.CARD,
        nullable=False,
    )
    checkout_session_id = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    payment_failures = relationship(
        "PaymentFailure", back_populates="transaction", cascade="all, delete-orphan"
    )

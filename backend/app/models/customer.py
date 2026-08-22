import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, String
from sqlalchemy.orm import relationship

from app.db import Base


class CustomerSegment(str, enum.Enum):
    HIGH_VALUE = "HIGH_VALUE"
    REGULAR = "REGULAR"
    LOW_VALUE = "LOW_VALUE"
    LOYAL = "LOYAL"
    AT_RISK = "AT_RISK"
    CHURNING = "CHURNING"
    NEW = "NEW"


class CommunicationChannel(str, enum.Enum):
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    SMS = "SMS"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(32), nullable=True)
    segment = Column(
        Enum(CustomerSegment, name="customer_segment_enum"),
        default=CustomerSegment.REGULAR,
        nullable=False,
        index=True,
    )
    ltv = Column(Float, default=0.0, nullable=False)
    churn_probability = Column(Float, default=0.1, nullable=False)
    preferred_channel = Column(
        Enum(CommunicationChannel, name="communication_channel_enum"),
        default=CommunicationChannel.WHATSAPP,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    transactions = relationship(
        "Transaction", back_populates="customer", cascade="all, delete-orphan"
    )
    recovery_cases = relationship(
        "RecoveryCase", back_populates="customer", cascade="all, delete-orphan"
    )

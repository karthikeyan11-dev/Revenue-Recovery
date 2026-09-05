import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"
    BLOCKED = "BLOCKED"


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(String(64), primary_key=True, index=True)
    leak_id = Column(
        String(64),
        ForeignKey("revenue_leaks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    customer_id = Column(
        String(64), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        default=CaseStatus.OPEN,
        nullable=False,
        index=True,
    )
    recovered_amount = Column(Float, default=0.0, nullable=False)
    recovery_cost = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    revenue_leak = relationship("RevenueLeak", back_populates="recovery_case")
    customer = relationship("Customer", back_populates="recovery_cases")
    recovery_actions = relationship(
        "RecoveryAction", back_populates="recovery_case", cascade="all, delete-orphan"
    )
    communication_events = relationship(
        "CommunicationEvent", back_populates="recovery_case", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="recovery_case", cascade="all, delete-orphan"
    )
    promises_to_pay = relationship(
        "PromiseToPay", back_populates="recovery_case", cascade="all, delete-orphan"
    )

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class PromiseStatus(str, enum.Enum):
    PENDING = "PENDING"
    KEPT = "KEPT"
    BROKEN = "BROKEN"


class PromiseToPay(Base):
    __tablename__ = "promise_to_pay"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(
        String(64),
        ForeignKey("recovery_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    committed_amount = Column(Float, nullable=False)
    committed_date = Column(DateTime, nullable=False)
    status = Column(
        Enum(PromiseStatus, name="promise_status_enum"),
        default=PromiseStatus.PENDING,
        nullable=False,
        index=True,
    )
    follow_up_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    recovery_case = relationship("RecoveryCase", back_populates="promises_to_pay")

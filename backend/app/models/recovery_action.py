import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class ActionType(str, enum.Enum):
    RETRY = "RETRY"
    SEND_PAYMENT_LINK = "SEND_PAYMENT_LINK"
    SEND_WHATSAPP = "SEND_WHATSAPP"
    SEND_EMAIL = "SEND_EMAIL"
    OFFER_INCENTIVE = "OFFER_INCENTIVE"
    WAIT = "WAIT"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class PolicyDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


class ActionOutcome(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    IGNORED = "IGNORED"
    BLOCKED = "BLOCKED"
    ESCALATED_WAITING = "ESCALATED_WAITING"


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(
        String(64), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    proposed_action = Column(
        Enum(ActionType, name="action_type_enum"),
        nullable=False,
    )
    policy_decision = Column(
        Enum(PolicyDecision, name="policy_decision_enum"),
        default=PolicyDecision.APPROVED,
        nullable=False,
        index=True,
    )
    policy_reasoning = Column(Text, nullable=True)
    executed_action = Column(String(64), nullable=True)
    incentive_percent = Column(Float, default=0.0, nullable=True)
    retry_delay_hours = Column(Integer, default=0, nullable=True)
    outcome = Column(
        Enum(ActionOutcome, name="action_outcome_enum"),
        default=ActionOutcome.PENDING,
        nullable=False,
    )
    execution_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    executed_at = Column(DateTime, nullable=True)

    # Relationships
    recovery_case = relationship("RecoveryCase", back_populates="recovery_actions")

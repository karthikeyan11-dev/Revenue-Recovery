import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.customer import CommunicationChannel


class SimulatedResponse(str, enum.Enum):
    IGNORED = "IGNORED"
    OPENED = "OPENED"
    CLICKED = "CLICKED"
    PAID = "PAID"
    DECLINED = "DECLINED"


class CommunicationEvent(Base):
    __tablename__ = "communication_events"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(
        String(64), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel = Column(
        Enum(CommunicationChannel, name="comm_event_channel_enum"),
        default=CommunicationChannel.WHATSAPP,
        nullable=False,
    )
    recipient = Column(String(255), nullable=False)
    template_id = Column(String(64), nullable=True)
    message_content = Column(Text, nullable=False)
    simulated_response = Column(
        Enum(SimulatedResponse, name="simulated_response_enum"),
        default=SimulatedResponse.IGNORED,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    recovery_case = relationship("RecoveryCase", back_populates="communication_events")

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(
        String(64), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent = Column(String(64), nullable=False, index=True)
    step_name = Column(String(64), nullable=False)
    input_summary = Column(Text, nullable=False)
    output_summary = Column(Text, nullable=False)
    decision = Column(String(64), nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)  # Primary empirical confidence
    empirical_confidence = Column(Float, nullable=True)
    llm_stated_confidence = Column(Float, nullable=True)
    precedent_sample_size = Column(Integer, default=0, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    recovery_case = relationship("RecoveryCase", back_populates="audit_logs")

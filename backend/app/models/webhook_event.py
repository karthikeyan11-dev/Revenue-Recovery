from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text

from app.db import Base


class RazorpayWebhookEvent(Base):
    """
    Persists raw, incoming Razorpay webhook payloads for idempotency, auditability, and debugging.
    """

    __tablename__ = "razorpay_webhook_events"

    id = Column(String(64), primary_key=True, index=True)
    event_id = Column(String(128), unique=True, index=True, nullable=False)
    event_type = Column(String(64), index=True, nullable=False)
    signature = Column(String(128), nullable=True)
    payload_json = Column(Text, nullable=False)
    processed = Column(Boolean, default=True, nullable=False)
    case_id = Column(String(64), nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

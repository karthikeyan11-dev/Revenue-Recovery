import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, Float, Integer, String

from app.db import Base


class StrategyType(str, enum.Enum):
    BASELINE_RETRY_ONCE = "BASELINE_RETRY_ONCE"
    AI_ORCHESTRATOR = "AI_ORCHESTRATOR"


class RecoveryMetricsRecord(Base):
    __tablename__ = "recovery_metrics"

    id = Column(String(64), primary_key=True, index=True)
    strategy_name = Column(
        Enum(StrategyType, name="strategy_type_enum"),
        nullable=False,
        index=True,
    )
    total_revenue_at_risk = Column(Float, nullable=False, default=0.0)
    total_recovered_revenue = Column(Float, nullable=False, default=0.0)
    recovery_rate_percent = Column(Float, nullable=False, default=0.0)
    total_cost = Column(Float, nullable=False, default=0.0)
    net_roi_percent = Column(Float, nullable=False, default=0.0)
    cases_count = Column(Integer, nullable=False, default=0)
    recovered_cases_count = Column(Integer, nullable=False, default=0)
    escalated_cases_count = Column(Integer, nullable=False, default=0)
    rejected_actions_count = Column(Integer, nullable=False, default=0)
    segment_breakdown = Column(JSON, nullable=True)  # List of {segment, at_risk, recovered, rate}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

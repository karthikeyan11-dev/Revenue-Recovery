from datetime import datetime

from pydantic import BaseModel

from app.models.customer import CustomerSegment
from app.models.recovery_action import ActionOutcome, ActionType, PolicyDecision
from app.models.recovery_case import CaseStatus
from app.models.revenue_leak import LeakType
from app.schemas.promise import PromiseToPaySummary


class CaseActionItem(BaseModel):
    id: str
    proposed_action: ActionType
    policy_decision: PolicyDecision
    policy_reasoning: str | None = None
    outcome: ActionOutcome
    incentive_percent: float | None = 0.0
    created_at: datetime


class CaseTimelineItem(BaseModel):
    id: str
    agent: str
    step_name: str
    input_summary: str
    output_summary: str
    decision: str | None = None
    confidence: float
    empirical_confidence: float | None = None
    llm_stated_confidence: float | None = None
    precedent_sample_size: int | None = 0
    timestamp: datetime


class RecoveryCaseSummary(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_segment: CustomerSegment
    leak_type: LeakType
    leak_amount: float
    recoverability_score: float
    status: CaseStatus
    recovered_amount: float
    recovery_cost: float
    has_sufficient_precedent: bool = True
    precedent_count: int = 0
    promise_status: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None


class RecoveryCaseDetail(RecoveryCaseSummary):
    actions: list[CaseActionItem] = []
    timeline: list[CaseTimelineItem] = []
    promises: list[PromiseToPaySummary] = []


class CasesListResponse(BaseModel):
    items: list[RecoveryCaseSummary]
    total: int
    open_count: int
    recovered_count: int
    escalated_count: int
    failed_count: int

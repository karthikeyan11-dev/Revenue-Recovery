from typing import Any, TypedDict

from app.models.payment_failure import PaymentFailure
from app.models.recovery_action import ActionOutcome, PolicyDecision
from app.schemas.customer import CustomerIntelligenceOutput
from app.schemas.detective import RevenueDetectiveOutput
from app.schemas.strategist import ProposedRecoveryAction


class RecoveryAgentState(TypedDict):
    """
    LangGraph shared state dictionary passed across agent nodes.
    """

    failure: PaymentFailure
    db: Any | None
    detective_output: RevenueDetectiveOutput | None
    intel_output: CustomerIntelligenceOutput | None
    proposed_action: ProposedRecoveryAction | None
    policy_decision: PolicyDecision | None
    policy_reasoning: str | None
    execution_outcome: ActionOutcome | None
    recovered: bool
    recovered_amount: float
    cost: float
    details: str
    communication_event_data: dict[str, Any] | None
    reproposal_count: int

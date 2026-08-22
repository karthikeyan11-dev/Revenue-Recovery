import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.recovery_detective import RevenueDetectiveAgent
from app.agents.recovery_strategist import RecoveryStrategistAgent
from app.executor.executor import ActionExecutor
from app.models.payment_failure import PaymentFailure
from app.models.recovery_action import ActionOutcome, PolicyDecision
from app.policy.engine import PolicyEngine
from app.schemas.customer_intel import CustomerIntelligenceOutput
from app.schemas.detective import RevenueDetectiveOutput
from app.schemas.strategist import ProposedRecoveryAction

logger = logging.getLogger("app.agents.graph")


class RecoveryAgentState(TypedDict):
    failure: PaymentFailure
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


def detective_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    output = RevenueDetectiveAgent.analyze(failure)
    return {"detective_output": output}


def customer_intel_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    customer = failure.transaction.customer
    output = CustomerIntelligenceAgent.profile(customer)
    return {"intel_output": output}


def strategist_node(state: RecoveryAgentState) -> dict[str, Any]:
    detective_out = state["detective_output"]
    intel_out = state["intel_output"]
    action = RecoveryStrategistAgent.propose_action(detective_out, intel_out)
    return {"proposed_action": action}


def policy_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    proposal = state["proposed_action"]
    intel = state["intel_output"]

    res = PolicyEngine.evaluate(
        proposal=proposal,
        amount=failure.transaction.amount,
        previous_attempts=failure.attempt_number,
        customer_churn_risk=intel.churn_probability if intel else 0.0,
    )
    return {
        "policy_decision": res.decision,
        "policy_reasoning": res.reasoning,
    }


def executor_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    proposal = state["proposed_action"]
    policy_decision = state["policy_decision"]
    customer = failure.transaction.customer

    res = ActionExecutor.execute(
        action_type=proposal.action_type,
        policy_decision=policy_decision,
        amount=failure.transaction.amount,
        failure_reason=failure.failure_reason,
        attempt_number=failure.attempt_number,
        incentive_percent=proposal.incentive_percent,
        retry_delay_hours=proposal.retry_delay_hours,
        channel=proposal.channel,
        customer_contact=customer.email,
    )

    return {
        "execution_outcome": res.outcome,
        "recovered": res.recovered,
        "recovered_amount": res.recovered_amount,
        "cost": res.cost,
        "details": res.details,
    }


def build_recovery_graph():
    workflow = StateGraph(RecoveryAgentState)

    workflow.add_node("detective", detective_node)
    workflow.add_node("customer_intel", customer_intel_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("executor", executor_node)

    workflow.set_entry_point("detective")
    workflow.add_edge("detective", "customer_intel")
    workflow.add_edge("customer_intel", "strategist")
    workflow.add_edge("strategist", "policy")
    workflow.add_edge("policy", "executor")
    workflow.add_edge("executor", END)

    return workflow.compile()

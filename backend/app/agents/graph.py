import logging
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.recovery_strategist import RecoveryStrategistAgent
from app.agents.revenue_detective import RevenueDetectiveAgent
from app.agents.state import RecoveryAgentState
from app.executor.executor import ActionExecutor
from app.models.recovery_action import PolicyDecision
from app.policy.engine import PolicyEngine

logger = logging.getLogger("app.agents.graph")


def detective_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    db = state.get("db")
    logger.info(
        f"[LangGraph:detective_node] Processing failure {failure.id} (reason: {failure.failure_reason.value})"
    )
    output = RevenueDetectiveAgent.analyze(failure, db=db)
    return {"detective_output": output}


def customer_intel_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    customer = failure.transaction.customer
    db = state.get("db")
    logger.info(
        f"[LangGraph:customer_intel_node] Profiling customer {customer.id} (failure: {failure.id})"
    )
    output = CustomerIntelligenceAgent.profile(customer, failure=failure, db=db)
    return {"intel_output": output}


def strategist_node(state: RecoveryAgentState) -> dict[str, Any]:
    detective_out = state["detective_output"]
    intel_out = state["intel_output"]
    failure = state["failure"]
    reproposal_count = state.get("reproposal_count", 0)
    is_reproposal = reproposal_count > 0
    logger.info(
        f"[LangGraph:strategist_node] Proposing recovery strategy for failure {failure.id} "
        f"(reason: {failure.failure_reason.value}, is_reproposal={is_reproposal})"
    )
    action = RecoveryStrategistAgent.propose_action(
        detective_output=detective_out,
        intel_output=intel_out,
        failure_reason=failure.failure_reason.value,
        is_reproposal=is_reproposal,
    )
    return {"proposed_action": action}


def policy_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    proposal = state["proposed_action"]
    intel = state["intel_output"]
    reproposal_count = state.get("reproposal_count", 0)

    logger.info(
        f"[LangGraph:policy_node] Evaluating proposal {proposal.action_type.value} against policy rules (reproposal_count={reproposal_count})"
    )
    res = PolicyEngine.evaluate(
        proposal=proposal,
        amount=failure.transaction.amount,
        previous_attempts=failure.attempt_number,
        payer_reliability_score=intel.payer_reliability_score if intel else 0.50,
    )

    new_reproposal_count = (
        reproposal_count + 1 if res.decision == PolicyDecision.REJECTED else reproposal_count
    )

    return {
        "policy_decision": res.decision,
        "policy_reasoning": res.reasoning,
        "reproposal_count": new_reproposal_count,
    }


def force_escalation_node(state: RecoveryAgentState) -> dict[str, Any]:
    logger.warning(
        "[LangGraph:force_escalation_node] Policy rejected re-proposal. Mandatory human escalation."
    )
    return {
        "policy_decision": PolicyDecision.ESCALATED,
        "policy_reasoning": "Policy rejected subsequent re-proposal attempt. Mandatory human escalation.",
    }


def route_after_policy(state: RecoveryAgentState) -> str:
    decision = state.get("policy_decision")
    reproposal_count = state.get("reproposal_count", 0)
    if decision == PolicyDecision.REJECTED:
        if reproposal_count <= 1:
            logger.info(
                "[LangGraph:route_after_policy] Policy REJECTED. Re-routing back to Strategist for exactly 1 re-proposal."
            )
            return "strategist"
        else:
            logger.warning(
                "[LangGraph:route_after_policy] Policy REJECTED subsequent attempt. Forcing escalation."
            )
            return "force_escalation"
    return "executor"


def executor_node(state: RecoveryAgentState) -> dict[str, Any]:
    failure = state["failure"]
    proposal = state["proposed_action"]
    policy_decision = state["policy_decision"]
    customer = failure.transaction.customer

    logger.info(
        f"[LangGraph:executor_node] Executing action {proposal.action_type.value} (policy: {policy_decision.value})"
    )
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
        "communication_event_data": res.communication_event_data,
    }


def build_recovery_graph():
    workflow = StateGraph(RecoveryAgentState)

    workflow.add_node("detective", detective_node)
    workflow.add_node("customer_intel", customer_intel_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("force_escalation", force_escalation_node)
    workflow.add_node("executor", executor_node)

    workflow.set_entry_point("detective")
    workflow.add_edge("detective", "customer_intel")
    workflow.add_edge("customer_intel", "strategist")
    workflow.add_edge("strategist", "policy")
    workflow.add_conditional_edges(
        "policy",
        route_after_policy,
        {
            "strategist": "strategist",
            "force_escalation": "force_escalation",
            "executor": "executor",
        },
    )
    workflow.add_edge("force_escalation", "executor")
    workflow.add_edge("executor", END)

    return workflow.compile()


# Compiled Singleton Graph
recovery_graph = build_recovery_graph()

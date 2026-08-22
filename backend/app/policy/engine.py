import logging

from app.models.recovery_action import ActionType, PolicyDecision
from app.policy.rules import (
    HIGH_VALUE_THRESHOLD,
    MAX_INCENTIVE_PERCENT,
    MAX_RETRY_ATTEMPTS,
)
from app.schemas.strategist import ProposedRecoveryAction

logger = logging.getLogger("app.policy.engine")


class PolicyEvaluationResult:
    def __init__(
        self,
        decision: PolicyDecision,
        reasoning: str,
        adjusted_incentive: float | None = None,
        violated_rule: str | None = None,
    ):
        self.decision = decision
        self.reasoning = reasoning
        self.adjusted_incentive = adjusted_incentive
        self.violated_rule = violated_rule


class PolicyEngine:
    """
    Deterministic Policy Engine.
    Enforces strict business guardrails without LLM reasoning.
    """

    @staticmethod
    def evaluate(
        proposal: ProposedRecoveryAction,
        amount: float,
        previous_attempts: int = 0,
        customer_churn_risk: float = 0.0,
    ) -> PolicyEvaluationResult:
        logger.info(
            f"Evaluating policy for action={proposal.action_type}, amount=₹{amount}, attempts={previous_attempts}"
        )

        # Rule 1: Strict Incentive Cap Enforcement
        if proposal.action_type == ActionType.OFFER_INCENTIVE:
            if proposal.incentive_percent > MAX_INCENTIVE_PERCENT:
                return PolicyEvaluationResult(
                    decision=PolicyDecision.REJECTED,
                    reasoning=f"Proposed incentive {proposal.incentive_percent}% exceeds policy cap of {MAX_INCENTIVE_PERCENT}%. Action blocked.",
                    violated_rule="MAX_INCENTIVE_PERCENT_EXCEEDED",
                )

        # Rule 2: Max Retry Attempt Bound
        if proposal.action_type == ActionType.RETRY:
            if previous_attempts >= MAX_RETRY_ATTEMPTS:
                return PolicyEvaluationResult(
                    decision=PolicyDecision.ESCALATED,
                    reasoning=f"Case reached {previous_attempts} attempts. Policy enforces max {MAX_RETRY_ATTEMPTS} automated retries. Escalating to human queue.",
                    violated_rule="MAX_RETRY_ATTEMPTS_EXCEEDED",
                )

        # Rule 3: High Value Transaction Protection Gate
        if amount >= HIGH_VALUE_THRESHOLD and customer_churn_risk > 0.35:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED,
                reasoning=f"Transaction value ₹{amount:,.2f} exceeds high-value threshold (₹{HIGH_VALUE_THRESHOLD:,.2f}) with elevated churn risk ({customer_churn_risk:.0%}). Escalating for white-glove manual handling.",
                violated_rule="HIGH_VALUE_HIGH_CHURN_GATE",
            )

        # Rule 4: Explicit Human Escalation Request
        if proposal.action_type == ActionType.ESCALATE_TO_HUMAN:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED,
                reasoning=f"Strategist explicitly recommended manual intervention: {proposal.reasoning}",
                violated_rule="STRATEGIST_ESCALATION_REQUEST",
            )

        # Default Approval
        return PolicyEvaluationResult(
            decision=PolicyDecision.APPROVED,
            reasoning=f"Action '{proposal.action_type.value}' complies with all deterministic policy guardrails.",
            adjusted_incentive=proposal.incentive_percent,
        )

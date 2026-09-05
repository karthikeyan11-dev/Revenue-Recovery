import logging

from app.models.recovery_action import ActionType, PolicyDecision
from app.policy.rules import (
    HIGH_VALUE_THRESHOLD,
    MAX_INCENTIVE_PERCENT,
    MAX_PROMISE_FOLLOWUPS,
    MAX_RETRY_ATTEMPTS,
    MIN_PRECEDENT_SAMPLE_SIZE,
    RULE_HIGH_VALUE_LOW_RELIABILITY,
    RULE_INSUFFICIENT_PRECEDENT,
    RULE_MAX_INCENTIVE_PERCENT,
    RULE_MAX_PROMISE_FOLLOWUPS,
    RULE_MAX_RETRY_ATTEMPTS,
    RULE_STRATEGIST_ESCALATION,
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
        payer_reliability_score: float = 0.50,
        previous_promise_followups: int = 0,
    ) -> PolicyEvaluationResult:
        logger.info(
            f"Evaluating policy for action={proposal.action_type}, amount=₹{amount}, attempts={previous_attempts}, "
            f"reliability={payer_reliability_score}, promise_followups={previous_promise_followups}, "
            f"insufficient_precedent={getattr(proposal, 'insufficient_precedent', False)}"
        )

        # Rule 0A: Insufficient Precedent in RAG Playbook (Escalate to human review)
        if getattr(proposal, "insufficient_precedent", False):
            retrieved_cnt = getattr(proposal, "retrieved_precedent_count", 0)
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED,
                reasoning=(
                    f"Insufficient precedent evidence in recovery playbook (retrieved {retrieved_cnt} cases, "
                    f"minimum required is {MIN_PRECEDENT_SAMPLE_SIZE}). Escalating to human review."
                ),
                violated_rule=RULE_INSUFFICIENT_PRECEDENT,
            )

        # Rule 0B: Broken Promise Follow-up Stopping Rule (Max 1 automated follow-up before mandatory human escalation)
        if previous_promise_followups >= MAX_PROMISE_FOLLOWUPS:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED,
                reasoning=(
                    f"Broken promise has already received {previous_promise_followups} automated follow-up attempt(s). "
                    f"Policy enforces strict limit of max {MAX_PROMISE_FOLLOWUPS} automated follow-up. Escalating to human queue."
                ),
                violated_rule=RULE_MAX_PROMISE_FOLLOWUPS,
            )

        # Rule 1: Strict Incentive Cap Enforcement
        if proposal.action_type == ActionType.OFFER_INCENTIVE:
            if proposal.incentive_percent > MAX_INCENTIVE_PERCENT:
                return PolicyEvaluationResult(
                    decision=PolicyDecision.REJECTED,
                    reasoning=f"Proposed incentive {proposal.incentive_percent}% exceeds policy cap of {MAX_INCENTIVE_PERCENT}%. Action blocked.",
                    violated_rule=RULE_MAX_INCENTIVE_PERCENT,
                )

        # Rule 2: Max Retry Attempt Bound
        if proposal.action_type == ActionType.RETRY:
            if previous_attempts >= MAX_RETRY_ATTEMPTS:
                return PolicyEvaluationResult(
                    decision=PolicyDecision.ESCALATED,
                    reasoning=f"Case reached {previous_attempts} attempts. Policy enforces max {MAX_RETRY_ATTEMPTS} automated retries. Escalating to human queue.",
                    violated_rule=RULE_MAX_RETRY_ATTEMPTS,
                )

        # Rule 3: High Value Transaction Protection Gate
        if amount >= HIGH_VALUE_THRESHOLD and payer_reliability_score < 0.50:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED,
                reasoning=(
                    f"Transaction value ₹{amount:,.2f} exceeds high-value threshold (₹{HIGH_VALUE_THRESHOLD:,.2f}) "
                    f"for low-reliability payer ({payer_reliability_score:.1%}). Escalating for white-glove manual handling."
                ),
                violated_rule=RULE_HIGH_VALUE_LOW_RELIABILITY,
            )

        # Rule 4: Explicit Human Escalation Request
        if proposal.action_type == ActionType.ESCALATE_TO_HUMAN:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED,
                reasoning=f"Strategist explicitly recommended manual intervention: {proposal.reasoning}",
                violated_rule=RULE_STRATEGIST_ESCALATION,
            )

        # Default Approval
        return PolicyEvaluationResult(
            decision=PolicyDecision.APPROVED,
            reasoning=f"Action '{proposal.action_type.value}' complies with all deterministic policy guardrails.",
            adjusted_incentive=proposal.incentive_percent,
        )

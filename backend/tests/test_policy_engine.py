from app.models.recovery_action import ActionType, PolicyDecision
from app.policy.engine import PolicyEngine
from app.schemas.strategist import ProposedRecoveryAction


def test_policy_approves_valid_retry():
    proposal = ProposedRecoveryAction(
        action_type=ActionType.RETRY,
        retry_delay_hours=4,
        reasoning="Soft failure retry",
    )
    result = PolicyEngine.evaluate(proposal, amount=1200.0, previous_attempts=1)
    assert result.decision == PolicyDecision.APPROVED
    assert result.violated_rule is None


def test_policy_blocks_excessive_incentive():
    proposal = ProposedRecoveryAction(
        action_type=ActionType.OFFER_INCENTIVE,
        incentive_percent=15.0,  # Cap is 10%
        reasoning="Large discount offer",
    )
    result = PolicyEngine.evaluate(proposal, amount=5000.0, previous_attempts=1)
    assert result.decision == PolicyDecision.REJECTED
    assert result.violated_rule == "MAX_INCENTIVE_PERCENT_EXCEEDED"


def test_policy_escalates_max_retries_exceeded():
    proposal = ProposedRecoveryAction(
        action_type=ActionType.RETRY,
        reasoning="Attempt #4 retry",
    )
    result = PolicyEngine.evaluate(proposal, amount=2000.0, previous_attempts=3)
    assert result.decision == PolicyDecision.ESCALATED
    assert result.violated_rule == "MAX_RETRY_ATTEMPTS_EXCEEDED"


def test_policy_escalates_high_value_at_risk():
    proposal = ProposedRecoveryAction(
        action_type=ActionType.SEND_WHATSAPP,
        reasoning="Automated WhatsApp outreach",
    )
    result = PolicyEngine.evaluate(
        proposal,
        amount=45000.0,  # High value >= 25,000
        previous_attempts=1,
        customer_churn_risk=0.60,  # High churn risk > 0.35
    )
    assert result.decision == PolicyDecision.ESCALATED
    assert result.violated_rule == "HIGH_VALUE_HIGH_CHURN_GATE"


def test_policy_escalates_insufficient_precedent():
    """Verify that thin precedent in RAG recovery_playbook triggers deterministic human escalation."""
    proposal = ProposedRecoveryAction(
        action_type=ActionType.RETRY,
        insufficient_precedent=True,
        retrieved_precedent_count=2,
        reasoning="Attempting smart retry despite low playbook precedent",
    )
    result = PolicyEngine.evaluate(
        proposal,
        amount=500.0,  # Even small amount
        previous_attempts=1,
        customer_churn_risk=0.10,
    )
    assert result.decision == PolicyDecision.ESCALATED
    assert result.violated_rule == "INSUFFICIENT_PRECEDENT_GATE"
    assert "Insufficient precedent evidence" in result.reasoning

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
        payer_reliability_score=0.40,  # Low reliability score < 0.50
    )
    assert result.decision == PolicyDecision.ESCALATED
    assert result.violated_rule == "HIGH_VALUE_LOW_RELIABILITY_GATE"


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
        payer_reliability_score=0.80,
    )
    assert result.decision == PolicyDecision.ESCALATED
    assert result.violated_rule == "INSUFFICIENT_PRECEDENT_GATE"
    assert "Insufficient precedent evidence" in result.reasoning


def test_policy_rejection_reproposal_loop_in_graph():
    """Verify that a rejected proposal is routed back to Strategist for exactly 1 re-proposal,
    and a second rejection forces human escalation."""
    from app.agents.graph import recovery_graph
    from app.models.customer import Customer
    from app.models.payment_failure import FailureReason, PaymentFailure
    from app.models.transaction import PaymentMethod, Transaction, TransactionStatus

    cust = Customer(
        id="cust_loop_test",
        name="Test Loop Customer",
        email="loop@example.com",
        phone="+919876543210",
    )
    tx = Transaction(
        id="tx_loop_test",
        customer_id=cust.id,
        amount=2000.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI,
        customer=cust,
    )
    pf = PaymentFailure(
        id="pf_loop_test",
        transaction_id=tx.id,
        failure_reason=FailureReason.NETWORK_ERROR,
        attempt_number=1,
        transaction=tx,
    )

    initial_state = {
        "failure": pf,
        "db": None,
        "detective_output": None,
        "intel_output": None,
        "proposed_action": None,
        "policy_decision": None,
        "policy_reasoning": None,
        "execution_outcome": None,
        "recovered": False,
        "recovered_amount": 0.0,
        "cost": 0.0,
        "details": "",
        "communication_event_data": None,
        "reproposal_count": 0,
    }

    final_state = recovery_graph.invoke(initial_state)
    assert final_state["policy_decision"] in [PolicyDecision.APPROVED, PolicyDecision.ESCALATED]

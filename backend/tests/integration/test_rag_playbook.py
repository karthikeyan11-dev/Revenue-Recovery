import pytest

from app.agents.recovery_analyst import RecoveryAnalystAgent
from app.agents.recovery_strategist import RecoveryStrategistAgent
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService
from app.models.customer import CommunicationChannel
from app.models.payment_failure import FailureReason
from app.models.recovery_action import PolicyDecision
from app.models.revenue_leak import LeakType
from app.policy.engine import PolicyEngine
from app.schemas.customer import CustomerIntelligenceOutput
from app.schemas.detective import RevenueDetectiveOutput


@pytest.fixture(autouse=True)
def clean_playbook():
    """Ensure ChromaDB playbook starts clean for every test."""
    RecoveryPlaybookService.reset_playbook()
    yield
    RecoveryPlaybookService.reset_playbook()


def test_chroma_playbook_cold_start():
    """Test empty playbook behavior."""
    assert RecoveryPlaybookService.get_playbook_count() == 0
    results = RecoveryPlaybookService.query_similar_cases(
        failure_reason="NETWORK_ERROR",
        k=5,
    )
    assert results == []


def test_chroma_playbook_insertion_and_query():
    """Test inserting resolved cases and querying similar precedents."""
    RecoveryPlaybookService.insert_resolved_case(
        case_id="case_001",
        failure_reason="NETWORK_ERROR",
        action_taken="RETRY",
        channel="NONE",
        outcome="SUCCESS",
        recovered_amount=1500.0,
    )
    RecoveryPlaybookService.insert_resolved_case(
        case_id="case_002",
        failure_reason="NETWORK_ERROR",
        action_taken="RETRY",
        channel="NONE",
        outcome="FAILED",
        recovered_amount=0.0,
    )

    assert RecoveryPlaybookService.get_playbook_count() == 2

    results = RecoveryPlaybookService.query_similar_cases(
        failure_reason="NETWORK_ERROR",
        k=5,
    )
    assert len(results) == 2
    case_ids = [r["case_id"] for r in results]
    assert "case_001" in case_ids
    assert "case_002" in case_ids


def test_strategist_cold_start_insufficient_precedent():
    """Verify that RecoveryStrategist flags insufficient_precedent when playbook has < 5 cases."""
    det_out = RevenueDetectiveOutput(
        failure_id="fail_101",
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=5000.0,
        confidence=0.75,
        recoverability_score=0.85,
        reasoning="Network glitch",
    )
    intel_out = CustomerIntelligenceOutput(
        customer_id="cust_101",
        payer_reliability_score=0.85,
        available_channels=["WHATSAPP", "SMS", "EMAIL"],
        confidence=0.70,
        insights="Loyal customer",
    )

    # Empty playbook
    proposal = RecoveryStrategistAgent.propose_action(
        detective_output=det_out,
        intel_output=intel_out,
        failure_reason=FailureReason.NETWORK_ERROR.value,
    )

    assert proposal.insufficient_precedent is True
    assert proposal.retrieved_precedent_count == 0
    # Cold start Laplace: (0 + 2) / (0 + 4) = 0.50
    assert proposal.confidence == 0.50
    assert proposal.llm_stated_confidence is not None

    # Test policy engine escalates this proposal
    policy_res = PolicyEngine.evaluate(proposal, amount=5000.0, previous_attempts=1)
    assert policy_res.decision == PolicyDecision.ESCALATED
    assert policy_res.violated_rule == "INSUFFICIENT_PRECEDENT_GATE"


def test_strategist_sufficient_precedent_and_analyst_write_back():
    """Verify that RecoveryAnalyst write-backs populate the playbook and allow Strategist autonomous actions."""
    # Write back 6 cases (5 recovered, 1 failed)
    for i in range(6):
        outcome = "SUCCESS" if i < 5 else "FAILED"
        RecoveryAnalystAgent.write_back_resolved_case(
            case_id=f"hist_case_{i}",
            failure_reason="INSUFFICIENT_FUNDS",
            action_taken="SEND_WHATSAPP",
            channel="WHATSAPP",
            outcome=outcome,
            recovered_amount=25000.0 if outcome == "SUCCESS" else 0.0,
        )

    assert RecoveryPlaybookService.get_playbook_count() == 6

    det_out = RevenueDetectiveOutput(
        failure_id="fail_202",
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=25000.0,
        confidence=0.80,
        recoverability_score=0.75,
        reasoning="Insufficient funds on debit card",
    )
    intel_out = CustomerIntelligenceOutput(
        customer_id="cust_202",
        payer_reliability_score=0.90,
        available_channels=["WHATSAPP", "SMS", "EMAIL"],
        confidence=0.80,
        insights="VIP customer",
    )

    proposal = RecoveryStrategistAgent.propose_action(
        detective_output=det_out,
        intel_output=intel_out,
        failure_reason="INSUFFICIENT_FUNDS",
    )

    assert proposal.insufficient_precedent is False
    assert proposal.retrieved_precedent_count == 5  # k=5 requested
    # Retrieved top 5 (4 or 5 successes). E.g. if 4 successes: (4+2)/(5+4) = 6/9 = 0.6667, if 5: 7/9 = 0.7778
    assert proposal.confidence >= 0.66

    # Test policy engine evaluates without triggering INSUFFICIENT_PRECEDENT_GATE
    policy_res = PolicyEngine.evaluate(
        proposal,
        amount=15000.0,  # Below 25,000 threshold
        previous_attempts=1,
    )
    assert policy_res.decision == PolicyDecision.APPROVED
    assert policy_res.violated_rule is None

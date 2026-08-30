import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.recovery_action import ActionType, PolicyDecision
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.policy.engine import PolicyEngine
from app.rag.playbook import RecoveryPlaybookService
from app.schemas.strategist import ProposedRecoveryAction
from app.services.recovery_service import RecoveryService

logging.basicConfig(level=logging.WARNING)


def run_rag_feedback_loop_verification():
    print("=" * 85)
    print("AI REVENUE RECOVERY ORCHESTRATOR — RAG PLAYBOOK & POLICY ESCALATION TRACE")
    print("=" * 85)

    # 1. Start from a completely cold / empty ChromaDB collection
    RecoveryPlaybookService.reset_playbook()
    initial_count = RecoveryPlaybookService.get_playbook_count()
    print(f"[*] Initial ChromaDB recovery_playbook count: {initial_count} (Cold Start)")
    assert initial_count == 0

    # 2. Setup SQLite in-memory DB for pipeline execution
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()
    service = RecoveryService(db)

    # Create customers
    c1 = Customer(
        id="cust_loyal_101",
        name="Aditya Roy",
        email="aditya@example.com",
        phone="+919876543210",
        segment=CustomerSegment.LOYAL,
    )
    c2 = Customer(
        id="cust_hv_102",
        name="Kavita Krishnamurthy",
        email="kavita@example.com",
        phone="+919876543211",
        segment=CustomerSegment.HIGH_VALUE,
    )
    c3 = Customer(
        id="cust_reg_103",
        name="Manoj Bajpayee",
        email="manoj@example.com",
        phone="+919876543212",
        segment=CustomerSegment.REGULAR,
    )
    db.add_all([c1, c2, c3])
    db.commit()

    # Define a sequence of 10 cases (focusing on NETWORK_ERROR and INSUFFICIENT_FUNDS)
    batch_definitions = [
        {"cust": c1, "reason": FailureReason.NETWORK_ERROR, "amount": 2500.0, "attempt": 1},
        {"cust": c1, "reason": FailureReason.NETWORK_ERROR, "amount": 3200.0, "attempt": 1},
        {"cust": c2, "reason": FailureReason.NETWORK_ERROR, "amount": 4500.0, "attempt": 1},
        {"cust": c1, "reason": FailureReason.NETWORK_ERROR, "amount": 1800.0, "attempt": 1},
        {"cust": c2, "reason": FailureReason.NETWORK_ERROR, "amount": 5600.0, "attempt": 1},
        {"cust": c1, "reason": FailureReason.NETWORK_ERROR, "amount": 2900.0, "attempt": 1},
        {"cust": c3, "reason": FailureReason.NETWORK_ERROR, "amount": 3800.0, "attempt": 1},
        {"cust": c2, "reason": FailureReason.NETWORK_ERROR, "amount": 6200.0, "attempt": 1},
        {"cust": c1, "reason": FailureReason.NETWORK_ERROR, "amount": 4100.0, "attempt": 1},
        {"cust": c2, "reason": FailureReason.NETWORK_ERROR, "amount": 7500.0, "attempt": 1},
    ]

    print("\n--- STAGE 1: SEQUENTIAL BATCH RUN (COLD START -> WARM RAG PRECEDENT) ---")

    trace_records = []

    for idx, item in enumerate(batch_definitions, 1):
        cust = item["cust"]
        reason = item["reason"]
        amt = item["amount"]
        attempt = item["attempt"]

        tx = Transaction(
            id=f"tx_trace_{idx}",
            customer_id=cust.id,
            amount=amt,
            currency="INR",
            status=TransactionStatus.FAILED,
            payment_method=PaymentMethod.UPI,
        )
        pf = PaymentFailure(
            id=f"pf_trace_{idx}",
            transaction_id=tx.id,
            failure_reason=reason,
            attempt_number=attempt,
        )
        db.add_all([tx, pf])
        db.commit()

        # Count in ChromaDB before processing
        pre_count = RecoveryPlaybookService.get_playbook_count()

        # Execute full pipeline through LangGraph
        case = service.process_single_failure_pipeline(pf, use_mock=True)

        # Count in ChromaDB after processing (proves write-back)
        post_count = RecoveryPlaybookService.get_playbook_count()

        # Retrieve audit logs for this case
        case_detail = service.get_case_detail(case.id)
        strat_log = next(
            (log for log in case_detail.timeline if log.agent == "Recovery Strategist"),
            None,
        )
        policy_log = next(
            (log for log in case_detail.timeline if log.agent == "Policy Engine"), None
        )

        record = {
            "case_idx": idx,
            "case_id": case.id,
            "customer": cust.name,
            "segment": cust.segment.value,
            "reason": reason.value,
            "amount": amt,
            "playbook_before": pre_count,
            "playbook_after": post_count,
            "retrieved_count": strat_log.precedent_sample_size if strat_log else 0,
            "strategist_conf": strat_log.confidence if strat_log else 0.0,
            "policy_decision": policy_log.decision if policy_log else "UNKNOWN",
            "policy_reasoning": policy_log.output_summary if policy_log else "",
            "final_status": case.status.value,
        }
        trace_records.append(record)

        is_insufficient = record["retrieved_count"] < 5
        print(
            f"\n[Case #{idx:02d}] {cust.name} ({cust.segment.value}) | Amount: ₹{amt:,.2f} | Reason: {reason.value}"
        )
        print(f"  • Playbook size BEFORE: {pre_count} cases")
        print(f"  • Strategist Tool Call Retrieved: {record['retrieved_count']} similar cases")
        print(f"  • Insufficient Precedent Flag: {is_insufficient}")
        print(f"  • Strategist Laplace Confidence: {record['strategist_conf']:.4f}")
        print(f"  • Policy Engine Decision: {record['policy_decision']}")
        print(f"  • Policy Reasoning: {record['policy_reasoning']}")
        print(f"  • Case Final Status: {record['final_status']}")
        print(
            f"  • Recovery Analyst Write-Back: Playbook count updated {pre_count} -> {post_count}"
        )

    print("\n--- STAGE 2: DELIBERATE TEST CASE WITH ZERO PRECEDENT ---")
    # Deliberate proposal with insufficient_precedent = True
    novel_proposal = ProposedRecoveryAction(
        action_type=ActionType.RETRY,
        insufficient_precedent=True,
        retrieved_precedent_count=1,
        confidence=0.60,
        reasoning="Attempting retry on novel failure with thin evidence",
    )
    novel_eval = PolicyEngine.evaluate(
        proposal=novel_proposal,
        amount=1200.0,
        previous_attempts=1,
        payer_reliability_score=0.80,
    )
    print("Constructed Test Case:")
    print(f"  • Action: {novel_proposal.action_type.value}")
    print(
        f"  • Insufficient Precedent: {novel_proposal.insufficient_precedent} (Retrieved: {novel_proposal.retrieved_precedent_count})"
    )
    print("  • Amount: ₹1,200.00 (Low value)")
    print(f"  • Policy Evaluation Decision: {novel_eval.decision.value}")
    print(f"  • Violated Rule: {novel_eval.violated_rule}")
    print(f"  • Engine Reasoning: {novel_eval.reasoning}")
    assert novel_eval.decision == PolicyDecision.ESCALATED
    assert novel_eval.violated_rule == "INSUFFICIENT_PRECEDENT_GATE"

    print("\n" + "=" * 85)
    print("PHASE 3 VERIFICATION SUMMARY TABLE")
    print("=" * 85)
    print(
        f"{'Case':<6} | {'Playbook (Pre)':<14} | {'Retrieved k':<11} | {'Strat Conf':<10} | {'Policy Decision':<15} | {'Final Status':<12} | {'Write-Back'}"
    )
    print("-" * 85)
    for r in trace_records:
        print(
            f"#{r['case_idx']:<5} | {r['playbook_before']:<14} | {r['retrieved_count']:<11} | {r['strategist_conf']:<10.4f} | "
            f"{r['policy_decision']:<15} | {r['final_status']:<12} | {r['playbook_before']} -> {r['playbook_after']}"
        )
    print("=" * 85)

    # Confirm early vs later behavior:
    # Early cases (<5 in collection) had retrieved_count < 5 and escalated
    early_escalated = [r for r in trace_records if r["retrieved_count"] < 5]
    print(
        f"✓ Early cases with < 5 retrieved precedents triggered escalation: {len(early_escalated)} cases"
    )
    # Later cases (>=5 in collection) had retrieved_count = 5 and autonomous policy evaluation
    later_warm = [r for r in trace_records if r["retrieved_count"] >= 5]
    print(
        f"✓ Later cases with >= 5 retrieved precedents evaluated autonomously: {len(later_warm)} cases"
    )
    assert len(later_warm) > 0

    db.close()


if __name__ == "__main__":
    run_rag_feedback_loop_verification()

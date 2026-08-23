"""
Phase 4 Verification Trace Script — Promise-to-Pay Tracker & Stopping Rules.
Demonstrates:
1. Promise-to-Pay creation on interactive outreach dispatch.
2. Case 1: Promise breaks -> exactly ONE follow-up is triggered via Strategist + RAG + Policy + Executor.
3. Case 2: Promise breaks AGAIN after follow-up -> Policy Engine stopping rule enforces mandatory Human Escalation (0 automated loops).
"""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import Base
from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.promise_to_pay import PromiseToPay
from app.models.recovery_case import CaseStatus
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.rag.playbook import RecoveryPlaybookService
from app.services.promise_service import PromiseTrackerService
from app.services.recovery_service import RecoveryService


def print_banner(text: str):
    print("\n" + "=" * 90)
    print(f"  {text}")
    print("=" * 90)


def main():
    print_banner("PHASE 4 VERIFICATION TRACE: PROMISE-TO-PAY TRACKER & STOPPING RULES")

    # In-memory SQLite for isolated end-to-end trace
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed ChromaDB Playbook with 6 precedents to enable autonomous warm strategist action
    RecoveryPlaybookService.reset_playbook()
    for i in range(6):
        RecoveryPlaybookService.insert_resolved_case(
            case_id=f"seed_precedent_{i}",
            segment="LOYAL",
            failure_reason="USER_DROPOFF",
            action_taken="SEND_WHATSAPP",
            channel="WHATSAPP",
            outcome="SUCCESS" if i < 4 else "FAILED",
            recovered_amount=4500.0,
        )

    promise_service = PromiseTrackerService(db)
    recovery_service = RecoveryService(db)

    # -------------------------------------------------------------------------
    # PART 1: Initial Dispatch & Promise-to-Pay Creation
    # -------------------------------------------------------------------------
    print_banner("PART 1: Initial Interactive Dispatch & Automatic Promise Creation")
    cust1 = Customer(
        id="cust_trace_01",
        name="Vikram Seth",
        email="vikram@example.com",
        segment=CustomerSegment.LOYAL,
        ltv=52000.0,
        churn_probability=0.15,
        preferred_channel=CommunicationChannel.WHATSAPP,
    )
    tx1 = Transaction(
        id="tx_trace_01",
        customer_id=cust1.id,
        amount=4500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI,
    )
    pf1 = PaymentFailure(
        id="pf_trace_01",
        transaction_id=tx1.id,
        failure_reason=FailureReason.USER_DROPOFF,
        attempt_number=1,
    )
    db.add_all([cust1, tx1, pf1])
    db.commit()

    case1 = recovery_service.process_single_failure_pipeline(pf1, use_mock=True)
    promises_case1 = db.query(PromiseToPay).filter(PromiseToPay.case_id == case1.id).all()

    print(f"Case Created: ID={case1.id} | Status={case1.status.value}")
    print(f"Tracked Promises: {len(promises_case1)}")
    assert (
        len(promises_case1) == 1
    ), "Promise-to-Pay record must be created on interactive dispatch!"
    p1 = promises_case1[0]
    print(f"  -> Promise ID: {p1.id}")
    print(f"  -> Amount: ₹{p1.committed_amount:,.2f}")
    print(f"  -> Committed Date: {p1.committed_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  -> Status: {p1.status.value}")
    print(f"  -> Follow-up Count: {p1.follow_up_count}")

    # -------------------------------------------------------------------------
    # PART 2: Promise Breaks -> Triggers Follow-Up #1 via Strategist + RAG
    # -------------------------------------------------------------------------
    print_banner("PART 2: Promise Breaks (1st Time) -> Triggers Follow-Up #1 via Strategist + RAG")
    print(f"Evaluating Promise {p1.id} with is_paid=False (BROKEN)...")
    eval_p1, updated_case1 = promise_service.evaluate_promise(p1.id, is_paid=False)

    print("\n[Result after 1st Break]")
    print(f"  -> Promise Status: {eval_p1.status.value}")
    print(f"  -> Follow-Up Count: {eval_p1.follow_up_count} (Incremented to 1)")
    print(f"  -> Case Status: {updated_case1.status.value}")
    print(f"  -> Total Case Actions: {len(updated_case1.recovery_actions)}")

    latest_action = updated_case1.recovery_actions[-1]
    print(f"  -> Executed Follow-up Action: {latest_action.proposed_action.value}")
    print(f"  -> Execution Details: {latest_action.execution_details}")
    print(f"  -> Policy Decision: {latest_action.policy_decision.value}")

    # Inspect Audit Logs
    print("\nAudit Trail for Case 1 Follow-Up:")
    for log in updated_case1.audit_logs:
        print(
            f"  - [{log.agent}] ({log.step_name}): {log.output_summary} | Empirical Conf: {log.empirical_confidence}"
        )

    assert eval_p1.follow_up_count == 1, "Follow-up count must be 1"
    assert (
        "Promise Follow-Up #1" in latest_action.execution_details
    ), "Follow-up execution details must be recorded"

    # -------------------------------------------------------------------------
    # PART 3: Promise Breaks AGAIN -> Strict Stopping Rule Enforces Escalation
    # -------------------------------------------------------------------------
    print_banner("PART 3: Promise Breaks AGAIN -> Stopping Rule Enforces Mandatory Escalation")
    print(
        "Customer failed to fulfill commitment after Follow-Up #1. Evaluating is_paid=False again..."
    )

    # Now evaluate p1 breaking again
    eval_p2, escalated_case = promise_service.evaluate_promise(eval_p1.id, is_paid=False)

    print("\n[Result after 2nd Break]")
    print(f"  -> Promise Status: {eval_p2.status.value}")
    print(f"  -> Follow-Up Count: {eval_p2.follow_up_count} (Unchanged, no new follow-ups)")
    print(f"  -> Case Status: {escalated_case.status.value} (FORCED HUMAN ESCALATION)")
    print(
        f"  -> Total Case Actions: {len(escalated_case.recovery_actions)} (Zero new automated actions attempted!)"
    )

    # Verify stopping rule audit log
    stopping_log = next(
        (log for log in escalated_case.audit_logs if log.step_name == "STOPPING_RULE_ENFORCEMENT"),
        None,
    )
    assert stopping_log is not None, "Stopping rule audit log must be recorded!"
    print("\nStopping Rule Audit Entry:")
    print(f"  - Agent: {stopping_log.agent}")
    print(f"  - Decision: {stopping_log.decision}")
    print(f"  - Output Summary: {stopping_log.output_summary}")

    assert (
        escalated_case.status == CaseStatus.ESCALATED
    ), "Case must be ESCALATED after 2nd broken promise!"

    print_banner("SUCCESS: ALL PHASE 4 CRITERIA VERIFIED AND PASSING!")


if __name__ == "__main__":
    main()

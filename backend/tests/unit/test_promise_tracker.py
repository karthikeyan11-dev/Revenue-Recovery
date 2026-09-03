from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService
from app.models.customer import Customer
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.promise_to_pay import PromiseStatus, PromiseToPay
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.policy.rules import RULE_MAX_PROMISE_FOLLOWUPS
from app.services.promise_service import PromiseTrackerService
from app.services.recovery_orchestrator import RecoveryOrchestratorService


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    # Ensure ChromaDB playbook has precedents for USER_DROPOFF and NETWORK_ERROR
    for i in range(6):
        RecoveryPlaybookService.insert_resolved_case(
            case_id=f"seed_case_ud_{i}",
            failure_reason="USER_DROPOFF",
            action_taken="SEND_WHATSAPP",
            channel="WHATSAPP",
            outcome="SUCCESS" if i < 4 else "FAILED",
            recovered_amount=3500.0,
        )
        RecoveryPlaybookService.insert_resolved_case(
            case_id=f"seed_case_ne_{i}",
            failure_reason="NETWORK_ERROR",
            action_taken="SEND_WHATSAPP",
            channel="WHATSAPP",
            outcome="SUCCESS" if i < 4 else "FAILED",
            recovered_amount=3000.0,
        )
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_promise_creation_on_dispatches(test_db):
    """Verify that when interactive outreach is executed, a PromiseToPay record is created."""
    service = RecoveryOrchestratorService(test_db)
    cust = Customer(
        id="cust_test_p1",
        name="Sunil Gavaskar",
        email="sunil@example.com",
        phone="+919876543210",
    )
    tx = Transaction(
        id="tx_test_p1",
        customer_id=cust.id,
        amount=3500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI,
    )
    pf = PaymentFailure(
        id="pf_test_p1",
        transaction_id=tx.id,
        failure_reason=FailureReason.USER_DROPOFF,
        attempt_number=1,
    )
    tx.customer = cust
    pf.transaction = tx
    test_db.add_all([cust, tx, pf])
    test_db.commit()

    case = service.process_single_failure_pipeline(pf, use_mock=True)
    assert case is not None
    assert len(case.promises_to_pay) == 1
    promise = case.promises_to_pay[0]
    assert promise.status in [PromiseStatus.PENDING, PromiseStatus.KEPT]
    assert promise.committed_amount == 3500.0
    assert promise.follow_up_count == 0


def test_promise_kept_resolution(test_db):
    """Verify that evaluating a promise as KEPT resolves the case with full recovered amount."""
    orchestrator = RecoveryOrchestratorService(test_db)
    tracker = PromiseTrackerService(test_db)

    cust = Customer(
        id="cust_test_p2",
        name="Kapil Dev",
        email="kapil@example.com",
        phone="+919876543210",
    )
    tx = Transaction(
        id="tx_test_p2",
        customer_id=cust.id,
        amount=5000.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI,
    )
    pf = PaymentFailure(
        id="pf_test_p2",
        transaction_id=tx.id,
        failure_reason=FailureReason.USER_DROPOFF,
        attempt_number=1,
    )
    tx.customer = cust
    pf.transaction = tx
    test_db.add_all([cust, tx, pf])
    test_db.commit()

    case = orchestrator.process_single_failure_pipeline(pf, use_mock=True)
    promise = case.promises_to_pay[0]

    # Evaluate as KEPT (Customer paid!)
    updated_promise, updated_case = tracker.evaluate_promise(promise.id, is_paid=True)
    assert updated_promise.status == PromiseStatus.KEPT
    assert updated_promise.resolved_at is not None
    assert updated_case.status == CaseStatus.RECOVERED
    assert updated_case.recovered_amount == 5000.0


def test_promise_broken_reinvokes_strategist_once(test_db):
    """Verify that a broken promise allows exactly 1 re-dispatch attempt."""
    cust = Customer(
        id="cust_test_p3",
        name="Rahul Dravid",
        email="rahul@example.com",
        phone="+919876543210",
    )
    tx = Transaction(
        id="tx_test_p3",
        customer_id=cust.id,
        amount=4500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI,
    )
    pf = PaymentFailure(
        id="pf_test_p3",
        transaction_id=tx.id,
        failure_reason=FailureReason.NETWORK_ERROR,
        attempt_number=1,
    )
    leak = RevenueLeak(
        id="leak_test_p3",
        failure_id=pf.id,
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=4500.0,
    )
    case = RecoveryCase(
        id="case_test_p3",
        leak_id=leak.id,
        customer_id=cust.id,
        status=CaseStatus.IN_PROGRESS,
    )
    promise = PromiseToPay(
        id="ptp_test_p3",
        case_id=case.id,
        committed_amount=4500.0,
        committed_date=datetime.utcnow() + timedelta(days=2),
        status=PromiseStatus.PENDING,
        follow_up_count=0,
    )
    test_db.add_all([cust, tx, pf, leak, case, promise])
    test_db.commit()

    promise_service = PromiseTrackerService(test_db)
    evaluated_p, updated_case = promise_service.evaluate_promise(promise.id, is_paid=False)

    # Promise is marked BROKEN
    assert evaluated_p.status == PromiseStatus.BROKEN
    # Follow-up count incremented to 1
    assert evaluated_p.follow_up_count == 1

    # Check that follow-up RecoveryAction was logged
    actions = updated_case.recovery_actions
    assert len(actions) >= 1
    assert "Promise Follow-Up #1" in actions[-1].execution_details


def test_broken_promise_second_break_forces_stopping_rule_escalation(test_db):
    """Verify that a second break after follow-up forces human escalation (stopping rule)."""
    cust = Customer(
        id="cust_test_p4",
        name="Sachin Tendulkar",
        email="sachin@example.com",
        phone="+919876543210",
    )
    tx = Transaction(
        id="tx_test_p4",
        customer_id=cust.id,
        amount=5000.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI,
    )
    pf = PaymentFailure(
        id="pf_test_p4",
        transaction_id=tx.id,
        failure_reason=FailureReason.NETWORK_ERROR,
        attempt_number=2,
    )
    leak = RevenueLeak(
        id="leak_test_p4",
        failure_id=pf.id,
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=5000.0,
    )
    case = RecoveryCase(
        id="case_test_p4",
        leak_id=leak.id,
        customer_id=cust.id,
        status=CaseStatus.IN_PROGRESS,
    )
    # Promise that already had 1 follow-up
    promise = PromiseToPay(
        id="ptp_test_p4",
        case_id=case.id,
        committed_amount=5000.0,
        committed_date=datetime.utcnow() + timedelta(days=2),
        status=PromiseStatus.PENDING,
        follow_up_count=1,  # Already used its 1 allowed follow-up!
    )
    test_db.add_all([cust, tx, pf, leak, case, promise])
    test_db.commit()

    promise_service = PromiseTrackerService(test_db)
    evaluated_p, updated_case = promise_service.evaluate_promise(promise.id, is_paid=False)

    # Must be marked BROKEN
    assert evaluated_p.status == PromiseStatus.BROKEN
    # Case MUST be escalated to human review, no further automated actions
    assert updated_case.status == CaseStatus.ESCALATED

    # Verify stopping rule audit log
    audit_logs = updated_case.audit_logs
    stopping_log = next(
        (log for log in audit_logs if log.step_name == "STOPPING_RULE_ENFORCEMENT"), None
    )
    assert stopping_log is not None
    assert stopping_log.decision == "ESCALATED"
    assert RULE_MAX_PROMISE_FOLLOWUPS in stopping_log.output_summary

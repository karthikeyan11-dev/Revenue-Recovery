import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent, SimulatedResponse
from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.recovery_action import ActionOutcome, ActionType, PolicyDecision, RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_complete_domain_model_persistence(db_session):
    # 1. Customer
    customer = Customer(
        id="cust_001",
        name="Aarav Sharma",
        email="aarav@example.com",
        phone="+919876543210",
        segment=CustomerSegment.HIGH_VALUE,
        ltv=45000.0,
        churn_probability=0.15,
        preferred_channel=CommunicationChannel.WHATSAPP,
    )
    db_session.add(customer)
    db_session.commit()

    # 2. Transaction
    tx = Transaction(
        id="txn_001",
        customer_id=customer.id,
        amount=12500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.CARD,
    )
    db_session.add(tx)
    db_session.commit()

    # 3. Payment Failure
    failure = PaymentFailure(
        id="fail_001",
        transaction_id=tx.id,
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        raw_error_code="ERR_INSUFF_FUNDS",
        attempt_number=1,
    )
    db_session.add(failure)
    db_session.commit()

    # 4. Revenue Leak
    leak = RevenueLeak(
        id="leak_001",
        failure_id=failure.id,
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=tx.amount,
        confidence=0.95,
        recoverability_score=0.85,
    )
    db_session.add(leak)
    db_session.commit()

    # 5. Recovery Case
    case = RecoveryCase(
        id="case_001",
        leak_id=leak.id,
        customer_id=customer.id,
        status=CaseStatus.IN_PROGRESS,
    )
    db_session.add(case)
    db_session.commit()

    # 6. Recovery Action
    action = RecoveryAction(
        id="act_001",
        case_id=case.id,
        proposed_action=ActionType.RETRY,
        policy_decision=PolicyDecision.APPROVED,
        outcome=ActionOutcome.SUCCESS,
        incentive_percent=0.0,
    )
    db_session.add(action)
    db_session.commit()

    # 7. Communication Event
    comm = CommunicationEvent(
        id="comm_001",
        case_id=case.id,
        channel=CommunicationChannel.WHATSAPP,
        recipient=customer.email,
        message_content="Test recovery reminder",
        simulated_response=SimulatedResponse.PAID,
    )
    db_session.add(comm)
    db_session.commit()

    # 8. Audit Log
    log = AuditLog(
        id="log_001",
        case_id=case.id,
        agent="Revenue Detective",
        step_name="LEAK_DETECTION",
        input_summary="Failure on card",
        output_summary="Classified soft decline",
        decision="APPROVED",
        confidence=0.95,
    )
    db_session.add(log)
    db_session.commit()

    # Verify query and relationships
    retrieved_case = db_session.query(RecoveryCase).filter(RecoveryCase.id == case.id).first()
    assert retrieved_case is not None
    assert retrieved_case.customer.name == "Aarav Sharma"
    assert retrieved_case.revenue_leak.amount == 12500.0
    assert len(retrieved_case.recovery_actions) == 1
    assert len(retrieved_case.communication_events) == 1
    assert len(retrieved_case.audit_logs) == 1

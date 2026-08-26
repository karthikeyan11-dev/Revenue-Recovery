import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.revenue_detective import RevenueDetectiveAgent
from app.database import Base
from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.repositories.recovery import RecoveryRepository


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
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_laplace_smoothing_formula():
    """Verify Laplace smoothing with prior_successes=2, prior_total=4."""
    # Cold start (0 cases): (0 + 2) / (0 + 4) = 0.50
    assert RecoveryRepository.calculate_laplace_confidence(0, 0) == 0.50

    # 10 cases, 8 successes: (8 + 2) / (10 + 4) = 10 / 14 = 0.7143
    assert RecoveryRepository.calculate_laplace_confidence(8, 10) == 0.7143

    # 10 cases, 2 successes: (2 + 2) / (10 + 4) = 4 / 14 = 0.2857
    assert RecoveryRepository.calculate_laplace_confidence(2, 10) == 0.2857

    # 100 cases, 90 successes: (90 + 2) / (100 + 4) = 92 / 104 = 0.8846
    assert RecoveryRepository.calculate_laplace_confidence(90, 100) == 0.8846


def test_empirical_sql_aggregate_queries(test_db):
    """Verify that RecoveryRepository SQL aggregates accurately count resolved cases and recoveries."""
    repo = RecoveryRepository(test_db)

    # 1. Create customers
    c_loyal = Customer(
        id="cust_loyal",
        name="Loyal User",
        email="loyal@example.com",
        segment=CustomerSegment.LOYAL,
        ltv=50000.0,
        churn_probability=0.10,
        preferred_channel=CommunicationChannel.WHATSAPP,
    )
    c_at_risk = Customer(
        id="cust_at_risk",
        name="At Risk User",
        email="risk@example.com",
        segment=CustomerSegment.AT_RISK,
        ltv=8000.0,
        churn_probability=0.75,
        preferred_channel=CommunicationChannel.EMAIL,
    )
    test_db.add_all([c_loyal, c_at_risk])
    test_db.commit()

    # 2. Seed past resolved cases for NETWORK_ERROR (3 resolved: 2 recovered, 1 failed)
    for i, status in enumerate([CaseStatus.RECOVERED, CaseStatus.RECOVERED, CaseStatus.FAILED]):
        tx = Transaction(
            id=f"tx_net_{i}",
            customer_id=c_loyal.id,
            amount=2000.0,
            currency="INR",
            status=TransactionStatus.FAILED,
            payment_method=PaymentMethod.UPI,
        )
        pf = PaymentFailure(
            id=f"pf_net_{i}",
            transaction_id=tx.id,
            failure_reason=FailureReason.NETWORK_ERROR,
            attempt_number=1,
        )
        leak = RevenueLeak(
            id=f"leak_net_{i}",
            failure_id=pf.id,
            leak_type=LeakType.TRANSACTION_FAILURE,
            amount=2000.0,
        )
        case = RecoveryCase(
            id=f"case_net_{i}",
            leak_id=leak.id,
            customer_id=c_loyal.id,
            status=status,
            recovered_amount=2000.0 if status == CaseStatus.RECOVERED else 0.0,
        )
        test_db.add_all([tx, pf, leak, case])

    # 3. Seed past resolved cases for EXPIRED_CARD (4 resolved: 1 recovered, 3 failed) under AT_RISK customer
    for i, status in enumerate(
        [CaseStatus.RECOVERED, CaseStatus.FAILED, CaseStatus.FAILED, CaseStatus.FAILED]
    ):
        tx = Transaction(
            id=f"tx_exp_{i}",
            customer_id=c_at_risk.id,
            amount=4000.0,
            currency="INR",
            status=TransactionStatus.FAILED,
            payment_method=PaymentMethod.CARD,
        )
        pf = PaymentFailure(
            id=f"pf_exp_{i}",
            transaction_id=tx.id,
            failure_reason=FailureReason.EXPIRED_CARD,
            attempt_number=1,
        )
        leak = RevenueLeak(
            id=f"leak_exp_{i}",
            failure_id=pf.id,
            leak_type=LeakType.SUBSCRIPTION_LAPSE,
            amount=4000.0,
        )
        case = RecoveryCase(
            id=f"case_exp_{i}",
            leak_id=leak.id,
            customer_id=c_at_risk.id,
            status=status,
            recovered_amount=4000.0 if status == CaseStatus.RECOVERED else 0.0,
        )
        test_db.add_all([tx, pf, leak, case])

    test_db.commit()

    # Query failure stats
    net_successes, net_total = repo.get_empirical_failure_recovery_stats(
        FailureReason.NETWORK_ERROR
    )
    assert net_total == 3
    assert net_successes == 2
    # Laplace confidence: (2 + 2) / (3 + 4) = 4 / 7 = 0.5714
    assert repo.calculate_laplace_confidence(net_successes, net_total) == 0.5714

    exp_successes, exp_total = repo.get_empirical_failure_recovery_stats(FailureReason.EXPIRED_CARD)
    assert exp_total == 4
    assert exp_successes == 1
    # Laplace confidence: (1 + 2) / (4 + 4) = 3 / 8 = 0.3750
    assert repo.calculate_laplace_confidence(exp_successes, exp_total) == 0.3750

    # Query segment stats
    loyal_succ, loyal_total = repo.get_empirical_segment_recovery_stats(CustomerSegment.LOYAL)
    assert loyal_total == 3
    assert loyal_succ == 2
    assert repo.calculate_laplace_confidence(loyal_succ, loyal_total) == 0.5714

    risk_succ, risk_total = repo.get_empirical_segment_recovery_stats(CustomerSegment.AT_RISK)
    assert risk_total == 4
    assert risk_succ == 1
    assert repo.calculate_laplace_confidence(risk_succ, risk_total) == 0.3750


def test_agents_compute_empirical_confidence(test_db):
    """Verify that RevenueDetective and CustomerIntelligence agents produce genuine empirical confidence."""
    # Seed 5 resolved cases for INSUFFICIENT_FUNDS (4 recovered, 1 failed) under HIGH_VALUE segment
    cust = Customer(
        id="cust_hv",
        name="High Value VIP",
        email="vip@example.com",
        segment=CustomerSegment.HIGH_VALUE,
        ltv=90000.0,
        churn_probability=0.08,
        preferred_channel=CommunicationChannel.WHATSAPP,
    )
    test_db.add(cust)
    test_db.commit()

    for i, status in enumerate(
        [
            CaseStatus.RECOVERED,
            CaseStatus.RECOVERED,
            CaseStatus.RECOVERED,
            CaseStatus.RECOVERED,
            CaseStatus.FAILED,
        ]
    ):
        tx = Transaction(
            id=f"tx_ins_{i}",
            customer_id=cust.id,
            amount=15000.0,
            currency="INR",
            status=TransactionStatus.FAILED,
            payment_method=PaymentMethod.CARD,
        )
        pf = PaymentFailure(
            id=f"pf_ins_{i}",
            transaction_id=tx.id,
            failure_reason=FailureReason.INSUFFICIENT_FUNDS,
            attempt_number=1,
        )
        leak = RevenueLeak(
            id=f"leak_ins_{i}",
            failure_id=pf.id,
            leak_type=LeakType.TRANSACTION_FAILURE,
            amount=15000.0,
        )
        case = RecoveryCase(
            id=f"case_ins_{i}",
            leak_id=leak.id,
            customer_id=cust.id,
            status=status,
            recovered_amount=15000.0 if status == CaseStatus.RECOVERED else 0.0,
        )
        test_db.add_all([tx, pf, leak, case])
    test_db.commit()

    # Now evaluate a new failure with the same failure reason
    new_tx = Transaction(
        id="tx_new_eval",
        customer_id=cust.id,
        amount=25000.0,
        currency="INR",
        status=TransactionStatus.FAILED,
    )
    new_pf = PaymentFailure(
        id="pf_new_eval",
        transaction_id=new_tx.id,
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_number=1,
    )
    new_tx.customer = cust
    new_pf.transaction = new_tx

    # 1. Revenue Detective
    det_out = RevenueDetectiveAgent.analyze(new_pf, db=test_db)
    # 4 successes / 5 total -> (4 + 2) / (5 + 4) = 6 / 9 = 0.6667
    assert det_out.confidence == 0.6667
    assert det_out.precedent_sample_size == 5
    assert det_out.llm_stated_confidence is not None

    # 2. Customer Intelligence
    intel_out = CustomerIntelligenceAgent.profile(cust, db=test_db)
    # 4 successes / 5 total -> (4 + 2) / (5 + 4) = 6 / 9 = 0.6667
    assert intel_out.confidence == 0.6667
    assert intel_out.precedent_sample_size == 5
    assert intel_out.llm_stated_confidence is not None

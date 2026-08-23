import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.revenue_detective import RevenueDetectiveAgent
from app.db import Base
from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.models.transaction import Transaction, TransactionStatus
from app.repositories.recovery_repository import RecoveryRepository

logging.basicConfig(level=logging.WARNING)


def run_empirical_confidence_trace():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()

    # Seed diverse historical precedent
    # Segment 1: LOYAL - 8 resolved cases (6 recovered, 2 failed)
    # Failure Reason 1: NETWORK_ERROR - 10 resolved cases (8 recovered, 2 failed)
    c_loyal = Customer(
        id="cust_loyal_1",
        name="Rohit Verma",
        email="rohit@example.com",
        segment=CustomerSegment.LOYAL,
        ltv=60000.0,
        churn_probability=0.12,
        preferred_channel=CommunicationChannel.WHATSAPP,
    )
    # Segment 2: AT_RISK - 12 resolved cases (3 recovered, 9 failed)
    # Failure Reason 2: EXPIRED_CARD - 6 resolved cases (1 recovered, 5 failed)
    c_at_risk = Customer(
        id="cust_risk_1",
        name="Sneha Patil",
        email="sneha@example.com",
        segment=CustomerSegment.AT_RISK,
        ltv=7500.0,
        churn_probability=0.78,
        preferred_channel=CommunicationChannel.EMAIL,
    )
    # Segment 3: HIGH_VALUE - 15 resolved cases (13 recovered, 2 failed)
    # Failure Reason 3: INSUFFICIENT_FUNDS - 20 resolved cases (11 recovered, 9 failed)
    c_high_val = Customer(
        id="cust_hv_1",
        name="Vikramaditya Singhania",
        email="vikram@example.com",
        segment=CustomerSegment.HIGH_VALUE,
        ltv=120000.0,
        churn_probability=0.05,
        preferred_channel=CommunicationChannel.WHATSAPP,
    )
    # Segment 4: CHURNING - 9 resolved cases (1 recovered, 8 failed)
    # Failure Reason 4: AUTHENTICATION_FAILED - 8 resolved cases (3 recovered, 5 failed)
    c_churning = Customer(
        id="cust_churn_1",
        name="Pooja Nair",
        email="pooja@example.com",
        segment=CustomerSegment.CHURNING,
        ltv=4200.0,
        churn_probability=0.92,
        preferred_channel=CommunicationChannel.SMS,
    )
    # Another LOYAL customer for invariance verification
    c_loyal_2 = Customer(
        id="cust_loyal_2",
        name="Deepak Joshi",
        email="deepak@example.com",
        segment=CustomerSegment.LOYAL,
        ltv=48000.0,
        churn_probability=0.15,
        preferred_channel=CommunicationChannel.WHATSAPP,
    )

    db.add_all([c_loyal, c_at_risk, c_high_val, c_churning, c_loyal_2])
    db.commit()

    def seed_cases(customer, failure_reason, total, recovered_count, leak_type):
        for i in range(total):
            status = CaseStatus.RECOVERED if i < recovered_count else CaseStatus.FAILED
            tx = Transaction(
                id=f"tx_hist_{failure_reason.value}_{customer.id}_{i}",
                customer_id=customer.id,
                amount=3000.0 + i * 200,
                currency="INR",
                status=TransactionStatus.FAILED,
            )
            pf = PaymentFailure(
                id=f"pf_hist_{failure_reason.value}_{customer.id}_{i}",
                transaction_id=tx.id,
                failure_reason=failure_reason,
                attempt_number=1,
            )
            leak = RevenueLeak(
                id=f"leak_hist_{failure_reason.value}_{customer.id}_{i}",
                failure_id=pf.id,
                leak_type=leak_type,
                amount=tx.amount,
            )
            case = RecoveryCase(
                id=f"case_hist_{failure_reason.value}_{customer.id}_{i}",
                leak_id=leak.id,
                customer_id=customer.id,
                status=status,
                recovered_amount=tx.amount if status == CaseStatus.RECOVERED else 0.0,
            )
            db.add_all([tx, pf, leak, case])
        db.commit()

    # Populate historical distributions
    # 1. NETWORK_ERROR under LOYAL: 10 cases (8 recovered, 2 failed)
    seed_cases(c_loyal, FailureReason.NETWORK_ERROR, 10, 8, LeakType.TRANSACTION_FAILURE)
    # 2. EXPIRED_CARD under AT_RISK: 6 cases (1 recovered, 5 failed)
    seed_cases(c_at_risk, FailureReason.EXPIRED_CARD, 6, 1, LeakType.SUBSCRIPTION_LAPSE)
    # 3. INSUFFICIENT_FUNDS under HIGH_VALUE: 20 cases (14 recovered, 6 failed)
    seed_cases(c_high_val, FailureReason.INSUFFICIENT_FUNDS, 20, 14, LeakType.TRANSACTION_FAILURE)
    # 4. AUTHENTICATION_FAILED under CHURNING: 8 cases (2 recovered, 6 failed)
    seed_cases(c_churning, FailureReason.AUTHENTICATION_FAILED, 8, 2, LeakType.TRANSACTION_FAILURE)

    print("=" * 85)
    print("AI REVENUE RECOVERY ORCHESTRATOR — 5-CASE EMPIRICAL CONFIDENCE TRACE")
    print("=" * 85)

    test_scenarios = [
        {
            "label": "Case 1: Transient Infrastructure Decline (Loyal Tier-1 Customer)",
            "customer": c_loyal,
            "failure_reason": FailureReason.NETWORK_ERROR,
            "amount": 1500.0,
            "attempt": 1,
        },
        {
            "label": "Case 2: Expired Subscription Instrument (At-Risk Churning Customer)",
            "customer": c_at_risk,
            "failure_reason": FailureReason.EXPIRED_CARD,
            "amount": 4200.0,
            "attempt": 2,
        },
        {
            "label": "Case 3: Soft Balance Decline (High-Value VIP Customer)",
            "customer": c_high_val,
            "failure_reason": FailureReason.INSUFFICIENT_FUNDS,
            "amount": 32000.0,
            "attempt": 1,
        },
        {
            "label": "Case 4: 3DS Auth Timeout (Churn-Prone Customer)",
            "customer": c_churning,
            "failure_reason": FailureReason.AUTHENTICATION_FAILED,
            "amount": 8900.0,
            "attempt": 1,
        },
        {
            "label": "Case 5: Transient Decline (Different Loyal Customer, Different ₹ Amount)",
            "customer": c_loyal_2,
            "failure_reason": FailureReason.NETWORK_ERROR,
            "amount": 18750.0,
            "attempt": 1,
        },
    ]

    results = []

    for idx, scen in enumerate(test_scenarios, 1):
        cust = scen["customer"]
        reason = scen["failure_reason"]
        amt = scen["amount"]
        attempt = scen["attempt"]

        tx = Transaction(
            id=f"tx_eval_{idx}",
            customer_id=cust.id,
            amount=amt,
            currency="INR",
            status=TransactionStatus.FAILED,
        )
        pf = PaymentFailure(
            id=f"pf_eval_{idx}",
            transaction_id=tx.id,
            failure_reason=reason,
            attempt_number=attempt,
        )
        tx.customer = cust
        pf.transaction = tx

        # Execute Revenue Detective
        det_out = RevenueDetectiveAgent.analyze(pf, db=db)
        # Execute Customer Intelligence
        intel_out = CustomerIntelligenceAgent.profile(cust, db=db)

        # Raw DB Stats
        repo = RecoveryRepository(db)
        det_succ, det_tot = repo.get_empirical_failure_recovery_stats(reason)
        seg_succ, seg_tot = repo.get_empirical_segment_recovery_stats(cust.segment)

        res_item = {
            "case_index": idx,
            "label": scen["label"],
            "customer_id": cust.id,
            "customer_name": cust.name,
            "segment": cust.segment.value,
            "failure_reason": reason.value,
            "amount": amt,
            "detective": {
                "sql_query": (
                    "SELECT COUNT(*) AS total, COUNT(CASE WHEN rc.status='RECOVERED' THEN 1 END) AS successes "
                    "FROM recovery_cases rc JOIN revenue_leaks rl ON rc.leak_id=rl.id "
                    "JOIN payment_failures pf ON rl.failure_id=pf.id "
                    f"WHERE pf.failure_reason = '{reason.value}' AND rc.status IN ('RECOVERED','FAILED','ESCALATED','BLOCKED')"
                ),
                "raw_counts": f"successes={det_succ}, total={det_tot}",
                "smoothing_formula": f"({det_succ} + 2) / ({det_tot} + 4)",
                "empirical_confidence": det_out.confidence,
                "llm_stated_confidence": det_out.llm_stated_confidence,
                "reasoning": det_out.reasoning,
            },
            "customer_intel": {
                "sql_query": (
                    "SELECT COUNT(*) AS total, COUNT(CASE WHEN rc.status='RECOVERED' THEN 1 END) AS successes "
                    "FROM recovery_cases rc JOIN customers c ON rc.customer_id=c.id "
                    f"WHERE c.segment = '{cust.segment.value}' AND rc.status IN ('RECOVERED','FAILED','ESCALATED','BLOCKED')"
                ),
                "raw_counts": f"successes={seg_succ}, total={seg_tot}",
                "smoothing_formula": f"({seg_succ} + 2) / ({seg_tot} + 4)",
                "empirical_confidence": intel_out.confidence,
                "llm_stated_confidence": intel_out.llm_stated_confidence,
                "insights": intel_out.insights,
            },
        }
        results.append(res_item)

        print(f"\n[{idx}] {scen['label']}")
        print(
            f"    Customer: {cust.name} ({cust.id}) | Segment: {cust.segment.value} | Amount: ₹{amt:,.2f}"
        )
        print(f"    Failure Reason: {reason.value} | Attempt #{attempt}")
        print("    " + "-" * 80)
        print("    [AGENT 1: REVENUE DETECTIVE]")
        print(f"      • SQL Query: {res_item['detective']['sql_query']}")
        print(f"      • Raw Aggregate: {res_item['detective']['raw_counts']}")
        print(
            f"      • Laplace Calculation: {res_item['detective']['smoothing_formula']} = {det_out.confidence:.4f}"
        )
        print(f"      • Logged LLM-Stated Confidence: {det_out.llm_stated_confidence} (Audit only)")
        print(f"      • Diagnostic Reasoning: {det_out.reasoning}")
        print("    [AGENT 2: CUSTOMER INTELLIGENCE]")
        print(f"      • SQL Query: {res_item['customer_intel']['sql_query']}")
        print(f"      • Raw Aggregate: {res_item['customer_intel']['raw_counts']}")
        print(
            f"      • Laplace Calculation: {res_item['customer_intel']['smoothing_formula']} = {intel_out.confidence:.4f}"
        )
        print(
            f"      • Logged LLM-Stated Confidence: {intel_out.llm_stated_confidence} (Audit only)"
        )
        print(f"      • Behavioral Insights: {intel_out.insights}")

    print("\n" + "=" * 85)
    print("INVARIANCE & VARIANCE PROOF MATRIX:")
    print("=" * 85)
    for r in results:
        print(
            f"Case #{r['case_index']} | Reason: {r['failure_reason']:<22} | "
            f"Det Conf: {r['detective']['empirical_confidence']:.4f} ({r['detective']['raw_counts']}) | "
            f"Seg: {r['segment']:<10} | Intel Conf: {r['customer_intel']['empirical_confidence']:.4f} ({r['customer_intel']['raw_counts']})"
        )
    print("-" * 85)
    print("✓ Case 1 vs Case 5 Invariance Check:")
    print(
        f"  Case 1 (Amount=₹{results[0]['amount']}, Customer={results[0]['customer_name']}): Detective Conf = {results[0]['detective']['empirical_confidence']:.4f}, Intel Conf = {results[0]['customer_intel']['empirical_confidence']:.4f}"
    )
    print(
        f"  Case 5 (Amount=₹{results[4]['amount']}, Customer={results[4]['customer_name']}): Detective Conf = {results[4]['detective']['empirical_confidence']:.4f}, Intel Conf = {results[4]['customer_intel']['empirical_confidence']:.4f}"
    )
    assert (
        results[0]["detective"]["empirical_confidence"]
        == results[4]["detective"]["empirical_confidence"]
    )
    assert (
        results[0]["customer_intel"]["empirical_confidence"]
        == results[4]["customer_intel"]["empirical_confidence"]
    )
    print(
        "  => EXACT MATCH confirmed (proves statistic derives strictly from aggregate historical distribution)."
    )
    print("=" * 85)

    db.close()


if __name__ == "__main__":
    run_empirical_confidence_trace()

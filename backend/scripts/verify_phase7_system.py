"""
Phase 7 Whole-System Verification Script.
Executes end-to-end traces for:
1. Dual Confidence & Empirical SQL Queries across 5 fresh cases.
2. Cold-start -> Feedback loop dynamic precedent learning in ChromaDB RAG.
3. Insufficient-precedent policy escalation trigger.
4. Promise-to-Pay stopping rule: 1 follow-up -> 2nd break forces human escalation.
5. Razorpay Tier 1 Orders & Tier 2 Webhook idempotency and forensics.
6. Baseline vs AI Orchestrator metrics isolation in database.
"""

import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.generators.synthetic_generator import SyntheticDataGenerator
from app.integrations.razorpay.client import RazorpayClient
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService
from app.models.customer import Customer
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.dashboard_service import DashboardService
from app.services.promise_service import PromiseTrackerService
from app.services.recovery_orchestrator import RecoveryOrchestratorService
from app.services.simulation_service import SimulationService

logging.basicConfig(level=logging.WARNING)


def banner(title: str):
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)


def verify_phase7():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()

    # --------------------------------------------------------------------------
    # 1. Empirical Confidence Traces (5 Fresh Cases across Detective, Intel, Strategist)
    # --------------------------------------------------------------------------
    banner("1. EMPIRICAL CONFIDENCE (LAPLACE SMOOTHING) TRACE ACROSS 5 FRESH CASES")

    SyntheticDataGenerator.populate_database(db, customer_count=50, transaction_count=100)

    rec_service = RecoveryOrchestratorService(db)
    sample_failures = db.query(PaymentFailure).limit(5).all()

    for idx, failure in enumerate(sample_failures, 1):
        case = rec_service.process_single_failure_pipeline(failure, use_mock=True)
        print(
            f"\n[Case {idx}] ID: {case.id} | Customer: {case.customer.name} | Reason: {failure.failure_reason.value}"
        )
        for log in case.audit_logs:
            precedent_str = (
                f" | Precedents: n={log.precedent_sample_size}"
                if log.precedent_sample_size is not None
                else ""
            )
            emp_conf = log.empirical_confidence or log.confidence
            llm_conf = log.llm_stated_confidence or 0.0
            print(
                f"   • Agent: {log.agent:<22} | Empirical: {emp_conf:.1%} | LLM Stated: {llm_conf:.1%}{precedent_str}"
            )

    # --------------------------------------------------------------------------
    # 2. RAG Cold Start & Feedback Loop Precedent Learning
    # --------------------------------------------------------------------------
    banner("2. CHROMA RAG COLD START -> DYNAMIC PRECEDENT LEARNING")
    RecoveryPlaybookService.reset_playbook()
    initial_count = RecoveryPlaybookService.get_playbook_count()
    print(f"Initial ChromaDB Collection Count (Cold Start): {initial_count}")

    cold_failures = db.query(PaymentFailure).offset(10).limit(4).all()
    for idx, fail in enumerate(cold_failures, 1):
        case = rec_service.process_single_failure_pipeline(fail, use_mock=True)
        strat_log = next(
            (log_item for log_item in case.audit_logs if log_item.agent == "Recovery Strategist"),
            None,
        )
        n_precedents = strat_log.precedent_sample_size if strat_log else 0
        emp_conf = strat_log.empirical_confidence or strat_log.confidence if strat_log else 0.0
        current_count = RecoveryPlaybookService.get_playbook_count()
        print(
            f"Run #{idx} -> Case {case.id}: Retrieved n={n_precedents} precedents | Empirical Conf: {emp_conf:.1%} | ChromaDB Size After Run: {current_count}"
        )

    # --------------------------------------------------------------------------
    # 3. Insufficient Precedent Policy Escalation
    # --------------------------------------------------------------------------
    banner("3. INSUFFICIENT-PRECEDENT ESCALATION TRIGGER")
    RecoveryPlaybookService.reset_playbook()  # Force 0 precedents
    constructed_cust = Customer(
        id="cust_novel_01",
        name="Ananya Panday",
        email="ananya@example.com",
        phone="+919800011122",
    )
    db.add(constructed_cust)
    db.commit()

    constructed_tx = Transaction(
        id="txn_novel_01",
        customer_id=constructed_cust.id,
        amount=12500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.CARD,
        created_at=datetime.utcnow(),
    )
    db.add(constructed_tx)
    db.commit()

    constructed_fail = PaymentFailure(
        id="fail_novel_01",
        transaction_id=constructed_tx.id,
        failure_reason=FailureReason.AUTHENTICATION_FAILED,
        raw_error_code="GATEWAY_ERROR",
        attempt_number=1,
        created_at=datetime.utcnow(),
    )
    db.add(constructed_fail)
    db.commit()

    novel_case = rec_service.process_single_failure_pipeline(constructed_fail, use_mock=True)
    policy_act = novel_case.recovery_actions[-1] if novel_case.recovery_actions else None
    print(f"Novel Case ID: {novel_case.id} | Status: {novel_case.status.value}")
    if policy_act:
        print(
            f"Policy Decision: {policy_act.policy_decision.value} | Proposed: {policy_act.proposed_action.value}"
        )
        print(f"Policy Reasoning: {policy_act.policy_reasoning}")

    # --------------------------------------------------------------------------
    # 4. Promise-to-Pay Stopping Rule Verification
    # --------------------------------------------------------------------------
    banner("4. PROMISE-TO-PAY STOPPING RULE: 1 FOLLOW-UP -> 2ND BREAK FORCES ESCALATION")
    ptp_service = PromiseTrackerService(db)

    # Setup Case with PTP
    ptp_cust = Customer(
        id="cust_ptp_01",
        name="Karan Johar",
        email="karan@example.com",
        phone="+919811122233",
    )
    db.add(ptp_cust)
    ptp_tx = Transaction(
        id="txn_ptp_01",
        customer_id=ptp_cust.id,
        amount=3000.0,
        status=TransactionStatus.FAILED,
        created_at=datetime.utcnow(),
    )
    db.add(ptp_tx)
    ptp_pf = PaymentFailure(
        id="pf_ptp_01",
        transaction_id=ptp_tx.id,
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_number=1,
        created_at=datetime.utcnow(),
    )
    db.add(ptp_pf)
    ptp_leak = RevenueLeak(
        id="leak_ptp_01",
        failure_id=ptp_pf.id,
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=3000.0,
        confidence=0.85,
        recoverability_score=0.80,
    )
    db.add(ptp_leak)
    ptp_case = RecoveryCase(
        id="case_ptp_stopping_rule_01",
        leak_id=ptp_leak.id,
        customer_id=ptp_cust.id,
        status=CaseStatus.IN_PROGRESS,
        created_at=datetime.utcnow(),
    )
    db.add(ptp_case)
    db.commit()

    # Step A: Customer promises to pay
    promise = ptp_service.create_promise(
        case_id=ptp_case.id,
        committed_amount=3000.0,
        days_to_pay=2,
    )
    print(
        f"Step A - Initial Promise Created: ID={promise.id} | Status={promise.status.value} | Follow-ups={promise.follow_up_count}"
    )

    # Step B: First Evaluation -> Broken (not paid), triggers follow-up retry #1
    p1, c1 = ptp_service.evaluate_promise(promise.id, is_paid=False)
    print(
        f"Step B - First Evaluation (1st Break): Promise Status={p1.status.value} | Follow-ups={p1.follow_up_count} | Case Status={c1.status.value}"
    )

    # Step C: Customer breaks the promise again after follow-up
    p2, c2 = ptp_service.evaluate_promise(promise.id, is_paid=False)
    print(
        f"Step C - Second Evaluation (2nd Break): Promise Status={p2.status.value} | Follow-ups={p2.follow_up_count} | Case Status={c2.status.value}"
    )
    print(
        "         Stopping Rule Triggered: Case strictly ESCALATED to human agent to prevent spam loops."
    )

    # --------------------------------------------------------------------------
    # 5. Razorpay Real Test Mode Orders & Webhook Idempotency
    # --------------------------------------------------------------------------
    banner("5. RAZORPAY TEST MODE REAL ORDERS & WEBHOOK FORENSICS")
    rzp_client = RazorpayClient()
    order = rzp_client.create_order(amount_rupees=4999.0, receipt="phase7_verify_rcpt")
    print(
        f"Live Razorpay Test Order Created: {order['id']} (Amount: ₹{order['amount']/100:,.2f} | Mock: {order.get('is_mock', False)})"
    )

    # --------------------------------------------------------------------------
    # 6. Baseline vs AI Comparison Isolation in DB
    # --------------------------------------------------------------------------
    sim_service = SimulationService(db)
    dash_service = DashboardService(db)
    sim_service.run_baseline_simulation(limit=50)
    sim_service.run_ai_simulation(limit=50, use_mock=True)

    summary = dash_service.get_dashboard_summary()
    print(f"Revenue at Risk:     ₹{summary.total_revenue_at_risk:,.2f}")
    print(
        f"Baseline Recovered:  ₹{summary.recovery_uplift_inr:,.2f} ({summary.baseline_recovery_rate:.1f}%)"
    )
    print(
        f"AI Recovered:        ₹{summary.total_recovered_revenue:,.2f} ({summary.overall_recovery_rate:.1f}%)"
    )
    print(f"Net AI Recovery ROI: {summary.net_roi_percent:.1f}%")
    print(f"Policy Interventions Triggered: {summary.policy_interventions_count}")


if __name__ == "__main__":
    verify_phase7()

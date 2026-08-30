#!/usr/bin/env python3
"""
Verification Script: 4 Payment-Native Customer Intelligence Signals.
Demonstrates:
  1. Payer Reliability Score (Laplace smoothed across real past transactions)
  2. Failure Timing Context (Hours since failure, 30-min burst detection)
  3. Alternate Rail Signal (Detects past successful rails differing from current failure)
  4. Available Contact Channels (Deterministic phone/email channel reachability)
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.recovery_strategist import RecoveryStrategistAgent
from app.database import Base
from app.models.customer import Customer
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.revenue_leak import LeakType
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.schemas.detective import RevenueDetectiveOutput


def run_verification():
    print("=" * 80)
    print("  VERIFYING 4 PAYMENT-NATIVE SIGNALS IN CUSTOMER INTELLIGENCE & STRATEGIST")
    print("=" * 80)

    # In-memory SQLite DB
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()

    # -------------------------------------------------------------------------
    # CASE 1: High-Reliability Repeat Customer with Past Alternate Rail
    # -------------------------------------------------------------------------
    print("\n--- CASE 1: Repeat Customer with Proven Track Record & Alternate Rail ---")
    c1 = Customer(
        id="cust_repeat_01",
        name="Rohit Sharma",
        email="rohit.sharma@example.com",
        phone="+919876543210",
    )
    db.add(c1)
    db.commit()

    # Seed 6 past transactions: 5 UPI successes, 1 CARD failure
    now = datetime.utcnow()
    for i in range(5):
        tx = Transaction(
            id=f"tx_c1_past_s_{i}",
            customer_id=c1.id,
            amount=4000.0,
            currency="INR",
            status=TransactionStatus.SUCCESS,
            payment_method=PaymentMethod.UPI,
            created_at=now - timedelta(days=30 - i * 5),
        )
        db.add(tx)
    tx_fail_old = Transaction(
        id="tx_c1_past_f_0",
        customer_id=c1.id,
        amount=5000.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.CARD,
        created_at=now - timedelta(days=2),
    )
    db.add(tx_fail_old)
    db.commit()

    # Current Failed Transaction: CARD failure (Expired Card / Bank Decline)
    tx1_curr = Transaction(
        id="tx_c1_curr",
        customer_id=c1.id,
        amount=12500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.CARD,
        created_at=now - timedelta(minutes=15),
    )
    pf1_curr = PaymentFailure(
        id="pf_c1_curr",
        transaction_id=tx1_curr.id,
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_number=1,
        created_at=now - timedelta(minutes=15),
    )
    tx1_curr.customer = c1
    pf1_curr.transaction = tx1_curr
    db.add_all([tx1_curr, pf1_curr])
    db.commit()

    intel1 = CustomerIntelligenceAgent.profile(c1, failure=pf1_curr, db=db)
    print(f"• Customer: {c1.name} ({c1.id})")
    print(
        f"• Total Past Attempts: {intel1.total_past_transactions}, Successes: {intel1.successful_past_transactions}"
    )
    print(
        f"• 1. Payer Reliability Score: {intel1.payer_reliability_score:.4f} (Laplace (5+2)/(7+4) = 7/11 = 0.6364)"
    )
    print(
        f"• 2. Failure Timing: {intel1.timing_band} (hours_since_failure={intel1.hours_since_failure:.2f}h, recent_burst={intel1.recent_failure_count})"
    )
    print(
        f"• 3. Alternate Rail Signal: has_alternate_rail={intel1.has_alternate_rail}, alternate_rails={intel1.alternate_rails}"
    )
    print(f"• 4. Available Contact Channels: {intel1.available_channels}")

    # Strategist proposal
    det1 = RevenueDetectiveOutput(
        failure_id=pf1_curr.id,
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=12500.0,
        confidence=0.75,
        recoverability_score=0.85,
        reasoning="Bank declined card authorization",
    )
    strat1 = RecoveryStrategistAgent.propose_action(
        det1, intel1, failure_reason=FailureReason.BANK_DECLINED
    )
    print(
        f"• Strategist Proposes: {strat1.action_type.value} via {strat1.channel} (Reason: {strat1.reasoning[:90]}...)"
    )

    assert intel1.payer_reliability_score == 0.6364
    assert intel1.has_alternate_rail is True
    assert "UPI" in intel1.alternate_rails
    assert intel1.timing_band == "RECENT"

    # -------------------------------------------------------------------------
    # CASE 2: New Customer with Laplace Neutral Baseline (0 past transactions)
    # -------------------------------------------------------------------------
    print("\n--- CASE 2: New Customer (Cold Start Laplace Smoothing) ---")
    c2 = Customer(
        id="cust_new_02",
        name="Ananya Verma",
        email="ananya.verma@example.com",
        phone="+919811223344",
    )
    db.add(c2)
    db.commit()

    tx2_curr = Transaction(
        id="tx_c2_curr",
        customer_id=c2.id,
        amount=2500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI,
        created_at=now - timedelta(hours=36),  # 36 hours ago -> STALE
    )
    pf2_curr = PaymentFailure(
        id="pf_c2_curr",
        transaction_id=tx2_curr.id,
        failure_reason=FailureReason.NETWORK_ERROR,
        attempt_number=1,
        created_at=now - timedelta(hours=36),
    )
    tx2_curr.customer = c2
    pf2_curr.transaction = tx2_curr
    db.add_all([tx2_curr, pf2_curr])
    db.commit()

    intel2 = CustomerIntelligenceAgent.profile(c2, failure=pf2_curr, db=db)
    print(f"• Customer: {c2.name} ({c2.id})")
    print(
        f"• Total Past Attempts: {intel2.total_past_transactions}, Successes: {intel2.successful_past_transactions}"
    )
    print(
        f"• 1. Payer Reliability Score: {intel2.payer_reliability_score:.4f} (Laplace (0+2)/(1+4) = 2/5 = 0.4000)"
    )
    print(
        f"• 2. Failure Timing: {intel2.timing_band} (hours_since_failure={intel2.hours_since_failure:.2f}h, recent_burst={intel2.recent_failure_count})"
    )
    print(
        f"• 3. Alternate Rail Signal: has_alternate_rail={intel2.has_alternate_rail}, alternate_rails={intel2.alternate_rails}"
    )
    print(f"• 4. Available Contact Channels: {intel2.available_channels}")

    assert intel2.payer_reliability_score == 0.4000
    assert intel2.has_alternate_rail is False
    assert intel2.timing_band == "STALE"

    # -------------------------------------------------------------------------
    # CASE 3: Single-Channel Customer (Email Only, No Phone)
    # -------------------------------------------------------------------------
    print("\n--- CASE 3: Single-Channel Customer (Email Only) ---")
    c3 = Customer(
        id="cust_email_only_03",
        name="Vikramaditya Singhania",
        email="vikramaditya@corporatemail.com",
        phone=None,  # No phone number
    )
    db.add(c3)
    db.commit()

    tx3_curr = Transaction(
        id="tx_c3_curr",
        customer_id=c3.id,
        amount=8500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.CARD,
        created_at=now - timedelta(minutes=5),
    )
    pf3_curr = PaymentFailure(
        id="pf_c3_curr",
        transaction_id=tx3_curr.id,
        failure_reason=FailureReason.EXPIRED_CARD,
        attempt_number=1,
        created_at=now - timedelta(minutes=5),
    )
    tx3_curr.customer = c3
    pf3_curr.transaction = tx3_curr
    db.add_all([tx3_curr, pf3_curr])
    db.commit()

    intel3 = CustomerIntelligenceAgent.profile(c3, failure=pf3_curr, db=db)
    print(f"• Customer: {c3.name} ({c3.id})")
    print(f"• 1. Payer Reliability Score: {intel3.payer_reliability_score:.4f}")
    print(f"• 2. Failure Timing: {intel3.timing_band}")
    print(f"• 3. Alternate Rail Signal: {intel3.has_alternate_rail}")
    print(f"• 4. Available Contact Channels: {intel3.available_channels}")

    det3 = RevenueDetectiveOutput(
        failure_id=pf3_curr.id,
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=8500.0,
        confidence=0.75,
        recoverability_score=0.80,
        reasoning="Expired card credentials",
    )
    strat3 = RecoveryStrategistAgent.propose_action(
        det3, intel3, failure_reason=FailureReason.EXPIRED_CARD
    )
    print(f"• Strategist Proposes: {strat3.action_type.value} via {strat3.channel}")

    assert intel3.available_channels == ["EMAIL"]
    assert "WHATSAPP" not in intel3.available_channels
    assert strat3.channel == "EMAIL"

    print("\n" + "=" * 80)
    print("  ALL 3 CASES VERIFIED SUCCESSFULLY AGAINST PAYMENT-NATIVE SIGNALS!")
    print("=" * 80)


if __name__ == "__main__":
    run_verification()

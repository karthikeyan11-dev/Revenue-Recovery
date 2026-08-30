import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.llm_client import LLMClient
from app.models.customer import Customer
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.transaction import Transaction, TransactionStatus
from app.repositories.recovery_repository import RecoveryRepository
from app.schemas.customer_intel import CustomerIntelligenceOutput

logger = logging.getLogger("app.agents.intelligence")


class CustomerIntelligenceAgent:
    """
    Customer Intelligence / Payment Signal Analyzer Agent.
    Evaluates 4 real, payment-native signals derived directly from actual stored transaction data:
      1. Payer Reliability Score (Laplace smoothed historical success rate)
      2. Failure Timing Context (recent vs. stale classification)
      3. Alternate Rail Signal (prior successful payment methods on record)
      4. Available Contact Channels (factual reachable channels from customer contact info)
    """

    @classmethod
    def profile(
        cls,
        customer: Customer,
        failure: PaymentFailure | None = None,
        db: Session | None = None,
    ) -> CustomerIntelligenceOutput:
        # ---------------------------------------------------------
        # Signal 1: Payer Reliability Score (0.0–1.0) with Laplace Smoothing
        # Formula: (successful_transactions + 2) / (total_transaction_attempts + 4)
        # ---------------------------------------------------------
        past_txs: list[Transaction] = []
        if db is not None:
            past_txs = (
                db.query(Transaction)
                .filter(Transaction.customer_id == customer.id)
                .all()
            )
        elif hasattr(customer, "transactions") and customer.transactions:
            past_txs = list(customer.transactions)

        total_past_transactions = len(past_txs)
        successful_past_transactions = sum(
            1 for t in past_txs if t.status == TransactionStatus.SUCCESS
        )

        payer_reliability_score = round(
            (successful_past_transactions + 2) / (total_past_transactions + 4),
            4,
        )

        # ---------------------------------------------------------
        # Signal 2: Failure Timing Context
        # Time elapsed since failure and count of failures in recent 30-min window
        # ---------------------------------------------------------
        now = datetime.utcnow()
        failure_time = (
            failure.created_at
            if failure and failure.created_at
            else now
        )
        hours_since_failure = max(
            0.0, round((now - failure_time).total_seconds() / 3600.0, 2)
        )

        recent_failure_count = 1
        if db is not None and failure is not None:
            window_start = failure_time - timedelta(minutes=30)
            window_end = failure_time + timedelta(minutes=30)
            recent_count = (
                db.query(func.count(PaymentFailure.id))
                .join(Transaction, PaymentFailure.transaction_id == Transaction.id)
                .filter(
                    Transaction.customer_id == customer.id,
                    PaymentFailure.created_at >= window_start,
                    PaymentFailure.created_at <= window_end,
                )
                .scalar()
            )
            recent_failure_count = int(recent_count or 1)

        timing_band = "RECENT" if hours_since_failure <= 2.0 else "STALE"

        # ---------------------------------------------------------
        # Signal 3: Alternate Rail Signal
        # Check if customer has successfully paid with another rail in transaction history
        # ---------------------------------------------------------
        current_failed_method = (
            failure.transaction.payment_method.value
            if failure and failure.transaction and failure.transaction.payment_method
            else None
        )

        successful_methods = {
            t.payment_method.value
            for t in past_txs
            if t.status == TransactionStatus.SUCCESS and t.payment_method
        }

        if current_failed_method:
            alternate_rails = sorted(list(successful_methods - {current_failed_method}))
        else:
            alternate_rails = sorted(list(successful_methods))

        has_alternate_rail = len(alternate_rails) > 0

        # ---------------------------------------------------------
        # Signal 4: Available Contact Channels (Factual, not scored)
        # ---------------------------------------------------------
        available_channels: list[str] = []
        has_phone = bool(customer.phone and customer.phone.strip())
        has_email = bool(customer.email and customer.email.strip())

        if has_phone:
            available_channels.extend(["WHATSAPP", "SMS"])
        if has_email:
            available_channels.append("EMAIL")

        if not available_channels:
            available_channels = ["EMAIL"]

        # ---------------------------------------------------------
        # Empirical Confidence Calculation
        # Grouped by failure_reason alone (same Bayesian Laplace prior)
        # ---------------------------------------------------------
        total_precedent = 0
        success_count = 0
        failure_reason: Any = (
            failure.failure_reason
            if failure
            else FailureReason.BANK_DECLINED
        )

        if db is not None:
            repo = RecoveryRepository(db)
            success_count, total_precedent = repo.get_empirical_failure_stats(failure_reason)
            empirical_confidence = repo.calculate_laplace_confidence(
                successes=success_count,
                total=total_precedent,
                prior_successes=2,
                prior_total=4,
            )
            logger.info(
                f"[CustomerIntelligence] Empirical confidence for failure reason '{failure_reason}': "
                f"{empirical_confidence:.4f} (successes={success_count}, total={total_precedent})"
            )
        else:
            empirical_confidence = RecoveryRepository.calculate_laplace_confidence(0, 0)

        # ---------------------------------------------------------
        # LLM Insights Generation
        # ---------------------------------------------------------
        if payer_reliability_score >= 0.70:
            base_insights = (
                f"High-reliability repeat payer ({payer_reliability_score:.1%}, {successful_past_transactions}/{total_past_transactions} past attempts). "
                f"Failure is likely transient. Channels available: {', '.join(available_channels)}."
            )
        elif has_alternate_rail:
            base_insights = (
                f"Moderate reliability ({payer_reliability_score:.1%}). Customer has proven alternate payment rail "
                f"({', '.join(alternate_rails)}). Propose switching rails via {available_channels[0]}."
            )
        else:
            base_insights = (
                f"New/volatile payer ({payer_reliability_score:.1%}, {successful_past_transactions}/{total_past_transactions} attempts). "
                f"Direct payment link via {available_channels[0]} recommended."
            )

        system_prompt = (
            "You are the Customer Intelligence AI agent in an autonomous revenue recovery system. "
            "Analyze the customer's payment-native signals (Payer Reliability Score, Timing Context, Alternate Rails, Available Channels) "
            "and generate concise, actionable recovery intelligence (1-2 sentences)."
        )
        user_prompt = (
            f"Customer Name: {customer.name}\n"
            f"Payer Reliability Score: {payer_reliability_score:.1%} ({successful_past_transactions}/{total_past_transactions} successful attempts)\n"
            f"Failure Timing Context: {timing_band} ({hours_since_failure:.1f}h elapsed, {recent_failure_count} attempt(s) in recent window)\n"
            f"Alternate Successful Rails: {', '.join(alternate_rails) if has_alternate_rail else 'None on record'}\n"
            f"Available Contact Channels: {', '.join(available_channels)}\n"
            f"Empirical Failure Cohort Recovery Rate: {empirical_confidence:.1%} (n={total_precedent})\n"
            "Provide customer-specific recovery intelligence."
        )

        llm_insights = LLMClient.generate_reasoning(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_text=base_insights,
        )

        llm_stated_conf = 0.85

        return CustomerIntelligenceOutput(
            customer_id=customer.id,
            payer_reliability_score=payer_reliability_score,
            total_past_transactions=total_past_transactions,
            successful_past_transactions=successful_past_transactions,
            timing_band=timing_band,
            hours_since_failure=hours_since_failure,
            recent_failure_count=recent_failure_count,
            has_alternate_rail=has_alternate_rail,
            alternate_rails=alternate_rails,
            available_channels=available_channels,
            confidence=empirical_confidence,
            insights=llm_insights,
            llm_stated_confidence=llm_stated_conf,
            precedent_sample_size=total_precedent,
        )

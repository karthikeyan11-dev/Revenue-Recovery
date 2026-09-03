import hashlib
import logging

from app.analytics.metrics import RecoveryMetricsCalculator
from app.executor.payment import PaymentSimulator
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.recovery_case import RecoveryCase
from app.schemas.analyst import StrategyMetrics

logger = logging.getLogger("app.analytics.baseline")


class BaselineSimulator:
    """
    Executes a naive retry-once benchmark against the failure dataset.
    Retries each failure blindly after 24h with no context, incentives, or multi-channel routing.
    Evaluates independently on identical failure/case cohorts.
    """

    @classmethod
    def evaluate_failure_baseline(
        cls,
        failure_reason: FailureReason,
        amount: float,
        failure_id: str | None = None,
    ) -> tuple[bool, float]:
        """
        Independently simulates naive retry-once baseline outcome for a single failure.
        - Blind retry attempt #1 with 24-hour delay
        - No multi-channel communications, no incentives, no RAG playbook
        - Deterministic seed derived from failure identity for 100% reproducibility
        """
        base_prob = PaymentSimulator.BASE_PROBABILITIES.get(failure_reason, 0.40)
        decay = 1.0 - (1 * 0.18)  # attempt 1 decay = 0.82
        effective_prob = base_prob * decay

        if failure_reason == FailureReason.INSUFFICIENT_FUNDS:
            effective_prob = min(0.60, effective_prob + 0.15)  # 24h banking recharge boost

        if failure_id:
            seed_str = f"baseline_eval_{failure_id}_{failure_reason.value if hasattr(failure_reason, 'value') else failure_reason}"
            hash_val = int(hashlib.md5(seed_str.encode("utf-8")).hexdigest(), 16)
            score = (hash_val % 1000000) / 1000000.0
            success = score < effective_prob
        else:
            success, _ = PaymentSimulator.simulate_retry(
                failure_reason=failure_reason,
                attempt_number=1,
                delay_hours=24,
            )

        recovered_amount = float(amount) if success else 0.0
        return success, recovered_amount

    @classmethod
    def evaluate_case_baseline(cls, case: RecoveryCase) -> tuple[bool, float]:
        """
        Independently simulates naive retry-once baseline outcome for a single RecoveryCase.
        Evaluates against the case's actual revenue leak amount and underlying failure reason.
        """
        if not case.revenue_leak:
            return False, 0.0

        amount = float(case.revenue_leak.amount or 0.0)
        failure = case.revenue_leak.payment_failure
        failure_reason = failure.failure_reason if failure else None

        if not failure_reason:
            return False, 0.0

        failure_id = failure.id if failure else case.id
        return cls.evaluate_failure_baseline(
            failure_reason=failure_reason,
            amount=amount,
            failure_id=failure_id,
        )

    @classmethod
    def run_benchmark(cls, failures: list[PaymentFailure]) -> tuple[StrategyMetrics, list[dict]]:
        logger.info(f"Running naive retry-once baseline benchmark on {len(failures)} failures...")

        total_at_risk = 0.0
        total_recovered = 0.0
        recovered_count = 0
        total_cost = len(failures) * 0.50  # 50 paise per retry attempt

        reason_data: dict[str, dict[str, float]] = {}

        for failure in failures:
            amount = float(failure.transaction.amount if failure.transaction else 0.0)
            total_at_risk += amount
            reason_str = (
                failure.failure_reason.value
                if hasattr(failure.failure_reason, "value")
                else str(failure.failure_reason)
            )

            if reason_str not in reason_data:
                reason_data[reason_str] = {"at_risk": 0.0, "recovered": 0.0}
            reason_data[reason_str]["at_risk"] += amount

            success, rec_amt = cls.evaluate_failure_baseline(
                failure_reason=failure.failure_reason,
                amount=amount,
                failure_id=failure.id,
            )

            if success:
                total_recovered += rec_amt
                recovered_count += 1
                reason_data[reason_str]["recovered"] += rec_amt

        breakdown = [
            {
                "failure_reason": r,
                "total_at_risk_inr": round(data["at_risk"], 2),
                "recovered_inr": round(data["recovered"], 2),
                "recovery_rate_percent": round(
                    (data["recovered"] / data["at_risk"] * 100.0) if data["at_risk"] > 0 else 0.0,
                    2,
                ),
            }
            for r, data in reason_data.items()
        ]

        metrics = RecoveryMetricsCalculator.calculate_strategy_metrics(
            strategy_name="BASELINE_RETRY_ONCE",
            total_at_risk=total_at_risk,
            total_recovered=total_recovered,
            total_cost=total_cost,
            cases_count=len(failures),
            recovered_cases_count=recovered_count,
            escalated_count=0,
            rejected_count=0,
        )
        return metrics, breakdown

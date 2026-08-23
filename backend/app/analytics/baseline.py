import logging

from app.analytics.metrics import RecoveryMetricsCalculator
from app.executor.payment_simulator import PaymentSimulator
from app.models.payment_failure import PaymentFailure
from app.schemas.analyst import StrategyMetrics

logger = logging.getLogger("app.analytics.baseline")


class BaselineSimulator:
    """
    Executes a naive retry-once benchmark against the failure dataset.
    Retries each failure blindly after 24h with no context, incentives, or multi-channel routing.
    """

    @staticmethod
    def run_benchmark(failures: list[PaymentFailure]) -> tuple[StrategyMetrics, list[dict]]:
        logger.info(f"Running naive retry-once baseline benchmark on {len(failures)} failures...")

        total_at_risk = 0.0
        total_recovered = 0.0
        recovered_count = 0
        total_cost = len(failures) * 0.50  # 50 paise per retry attempt

        segment_data: dict[str, dict[str, float]] = {}

        for failure in failures:
            amount = failure.transaction.amount
            total_at_risk += amount
            seg = (
                failure.transaction.customer.segment.value
                if failure.transaction and failure.transaction.customer
                else "REGULAR"
            )

            if seg not in segment_data:
                segment_data[seg] = {"at_risk": 0.0, "recovered": 0.0}
            segment_data[seg]["at_risk"] += amount

            # Naive retry: Attempt #1 after 24 hours
            success, _ = PaymentSimulator.simulate_retry(
                failure_reason=failure.failure_reason,
                attempt_number=1,
                delay_hours=24,
            )

            if success:
                total_recovered += amount
                recovered_count += 1
                segment_data[seg]["recovered"] += amount

        segment_breakdown = [
            {
                "segment": seg,
                "total_at_risk_inr": round(data["at_risk"], 2),
                "recovered_inr": round(data["recovered"], 2),
                "recovery_rate_percent": round(
                    (data["recovered"] / data["at_risk"] * 100.0) if data["at_risk"] > 0 else 0.0,
                    2,
                ),
            }
            for seg, data in segment_data.items()
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
        return metrics, segment_breakdown

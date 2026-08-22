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
    def run_benchmark(failures: list[PaymentFailure]) -> StrategyMetrics:
        logger.info(f"Running naive retry-once baseline benchmark on {len(failures)} failures...")

        total_at_risk = 0.0
        total_recovered = 0.0
        recovered_count = 0
        total_cost = len(failures) * 0.50  # 50 paise per retry attempt

        for failure in failures:
            amount = failure.transaction.amount
            total_at_risk += amount

            # Naive retry: Attempt #1 after 24 hours
            success, _ = PaymentSimulator.simulate_retry(
                failure_reason=failure.failure_reason,
                attempt_number=1,
                delay_hours=24,
            )

            if success:
                total_recovered += amount
                recovered_count += 1

        return RecoveryMetricsCalculator.calculate_strategy_metrics(
            strategy_name="BASELINE_RETRY_ONCE",
            total_at_risk=total_at_risk,
            total_recovered=total_recovered,
            total_cost=total_cost,
            cases_count=len(failures),
            recovered_cases_count=recovered_count,
            escalated_count=0,
            rejected_count=0,
        )

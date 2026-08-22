import logging

from app.analytics.metrics import RecoveryMetricsCalculator
from app.schemas.analyst import BaselineComparisonResult, StrategyMetrics

logger = logging.getLogger("app.agents.analyst")


class RecoveryAnalystAgent:
    """
    Recovery Analyst Agent Node.
    Analyzes aggregate batch performance and generates executive comparative takeaways.
    """

    @classmethod
    def evaluate_performance(
        cls,
        baseline_metrics: StrategyMetrics,
        ai_metrics: StrategyMetrics,
    ) -> BaselineComparisonResult:
        return RecoveryMetricsCalculator.compare(baseline_metrics, ai_metrics)

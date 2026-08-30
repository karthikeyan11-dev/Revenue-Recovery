import logging

from app.analytics.metrics import RecoveryMetricsCalculator
from app.rag.playbook import RecoveryPlaybookService
from app.schemas.analyst import BaselineComparisonResult, StrategyMetrics

logger = logging.getLogger("app.agents.analyst")


class RecoveryAnalystAgent:
    """
    Recovery Analyst Agent Node.
    Analyzes aggregate batch performance and closes the RAG learning loop by writing back
    resolved case outcomes into the ChromaDB recovery_playbook collection.
    """

    @classmethod
    def evaluate_performance(
        cls,
        baseline_metrics: StrategyMetrics,
        ai_metrics: StrategyMetrics,
    ) -> BaselineComparisonResult:
        return RecoveryMetricsCalculator.compare(baseline_metrics, ai_metrics)

    @classmethod
    def write_back_resolved_case(
        cls,
        case_id: str,
        failure_reason: str,
        action_taken: str,
        channel: str | None,
        outcome: str,
        recovered_amount: float,
        segment: str | None = None,
    ) -> None:
        """
        Inserts a resolved case into the ChromaDB recovery_playbook collection.
        This closes the feedback loop so that subsequent cases can retrieve grounded precedent.
        """
        logger.info(
            f"[RecoveryAnalyst] Writing back resolved case {case_id} to ChromaDB recovery_playbook "
            f"(Reason: {failure_reason}, Action: {action_taken}, Outcome: {outcome}, Recovered: ₹{recovered_amount:,.2f})"
        )
        RecoveryPlaybookService.insert_resolved_case(
            case_id=case_id,
            failure_reason=failure_reason,
            action_taken=action_taken,
            channel=channel,
            outcome=outcome,
            recovered_amount=recovered_amount,
            segment=segment,
        )

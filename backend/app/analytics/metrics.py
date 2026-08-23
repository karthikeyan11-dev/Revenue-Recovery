from app.schemas.analyst import BaselineComparisonResult, StrategyMetrics


class RecoveryMetricsCalculator:
    """
    Deterministic recovery metrics & ROI engine.
    Calculates actual ₹ recovered, ROI, and comparative uplift.
    """

    @staticmethod
    def calculate_strategy_metrics(
        strategy_name: str,
        total_at_risk: float,
        total_recovered: float,
        total_cost: float,
        cases_count: int,
        recovered_cases_count: int,
        escalated_count: int = 0,
        rejected_count: int = 0,
    ) -> StrategyMetrics:
        recovery_rate = (total_recovered / total_at_risk * 100.0) if total_at_risk > 0 else 0.0
        net_roi = (
            ((total_recovered - total_cost) / total_at_risk * 100.0) if total_at_risk > 0 else 0.0
        )

        return StrategyMetrics(
            strategy_name=strategy_name,
            total_revenue_at_risk=round(total_at_risk, 2),
            total_recovered_revenue=round(total_recovered, 2),
            recovery_rate_percent=round(recovery_rate, 2),
            total_cost=round(total_cost, 2),
            net_roi_percent=round(net_roi, 2),
            cases_count=cases_count,
            recovered_cases_count=recovered_cases_count,
            escalated_cases_count=escalated_count,
            rejected_actions_count=rejected_count,
        )

    @classmethod
    def compare(
        cls,
        baseline: StrategyMetrics,
        ai_orchestrator: StrategyMetrics,
    ) -> BaselineComparisonResult:
        uplift_inr = ai_orchestrator.total_recovered_revenue - baseline.total_recovered_revenue
        uplift_percent = ai_orchestrator.recovery_rate_percent - baseline.recovery_rate_percent

        findings: list[str] = [
            f"AI Orchestrator recovered ₹{ai_orchestrator.total_recovered_revenue:,.2f} vs. Baseline ₹{baseline.total_recovered_revenue:,.2f} (Net Gain: ₹{uplift_inr:,.2f}).",
            f"Recovery Rate improved from {baseline.recovery_rate_percent:.1f}% to {ai_orchestrator.recovery_rate_percent:.1f}% (+{uplift_percent:.1f}% absolute uplift).",
            f"Deterministic Policy Engine intervened on {ai_orchestrator.rejected_actions_count} unsafe actions and routed {ai_orchestrator.escalated_cases_count} high-value cases to human review.",
        ]

        return BaselineComparisonResult(
            baseline=baseline,
            ai_orchestrator=ai_orchestrator,
            uplift_inr=round(uplift_inr, 2),
            uplift_percent=round(uplift_percent, 2),
            key_findings=findings,
        )

import logging

from sqlalchemy.orm import Session

from app.analytics.baseline import BaselineSimulator
from app.analytics.metrics import RecoveryMetricsCalculator
from app.models.payment_failure import PaymentFailure
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.repositories.recovery_repository import RecoveryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.analyst import StrategyMetrics
from app.schemas.dashboard import DashboardMetricsResponse, RecoveryComparisonChartItem
from app.services.recovery_service import RecoveryService

logger = logging.getLogger("app.services.analytics")


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.recovery_repo = RecoveryRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.recovery_service = RecoveryService(db)

    def run_ai_simulation(self, limit: int | None = None, use_mock: bool = True) -> StrategyMetrics:
        failures = self.transaction_repo.get_unprocessed_failures(limit=limit)
        if not failures:
            # If all are already processed, get recent failures
            failures = self.db.query(PaymentFailure).limit(limit or 100).all()

        logger.info(f"Running AI Orchestrator simulation on {len(failures)} failures...")

        total_at_risk = 0.0
        total_recovered = 0.0
        total_cost = 0.0
        recovered_cases = 0
        escalated_cases = 0
        rejected_actions = 0

        for fail in failures:
            total_at_risk += fail.transaction.amount
            case = self.recovery_service.process_single_failure_pipeline(fail, use_mock=use_mock)

            if case.status == CaseStatus.RECOVERED:
                total_recovered += case.recovered_amount
                total_cost += case.recovery_cost
                recovered_cases += 1
            elif case.status == CaseStatus.ESCALATED:
                escalated_cases += 1
            elif case.status == CaseStatus.BLOCKED:
                rejected_actions += 1

        return RecoveryMetricsCalculator.calculate_strategy_metrics(
            strategy_name="AI_ORCHESTRATOR",
            total_at_risk=total_at_risk,
            total_recovered=total_recovered,
            total_cost=total_cost,
            cases_count=len(failures),
            recovered_cases_count=recovered_cases,
            escalated_count=escalated_cases,
            rejected_count=rejected_actions,
        )

    def run_baseline_simulation(self, limit: int | None = None) -> StrategyMetrics:
        failures = self.db.query(PaymentFailure).limit(limit or 100).all()
        return BaselineSimulator.run_benchmark(failures)

    def get_dashboard_summary(self) -> DashboardMetricsResponse:
        cases = self.db.query(RecoveryCase).all()

        if not cases:
            # If no simulation run yet, return clean zero state
            return DashboardMetricsResponse(
                total_revenue_at_risk=0.0,
                total_recovered_revenue=0.0,
                overall_recovery_rate=0.0,
                net_roi_percent=0.0,
                baseline_recovery_rate=0.0,
                recovery_uplift_inr=0.0,
                active_cases_count=0,
                escalated_cases_count=0,
                policy_interventions_count=0,
                comparison_chart=[],
            )

        total_at_risk = sum(c.revenue_leak.amount for c in cases if c.revenue_leak)
        total_recovered = sum(c.recovered_amount for c in cases)
        total_cost = sum(c.recovery_cost for c in cases)

        recovery_rate = (total_recovered / total_at_risk * 100.0) if total_at_risk > 0 else 0.0
        net_roi = (
            ((total_recovered - total_cost) / total_at_risk * 100.0) if total_at_risk > 0 else 0.0
        )

        # Naive baseline estimation against same amount: ~25% recovery
        baseline_rate = 24.5
        baseline_recovered = total_at_risk * (baseline_rate / 100.0)
        uplift_inr = max(0.0, total_recovered - baseline_recovered)

        active_count = sum(
            1 for c in cases if c.status in [CaseStatus.OPEN, CaseStatus.IN_PROGRESS]
        )
        escalated_count = sum(1 for c in cases if c.status == CaseStatus.ESCALATED)
        blocked_count = sum(1 for c in cases if c.status == CaseStatus.BLOCKED)

        # Segment breakdown for comparison chart
        segments = ["HIGH_VALUE", "LOYAL", "REGULAR", "AT_RISK", "CHURNING", "LOW_VALUE"]
        chart_items: list[RecoveryComparisonChartItem] = []

        for seg in segments:
            seg_cases = [c for c in cases if c.customer and c.customer.segment.value == seg]
            seg_at_risk = sum(c.revenue_leak.amount for c in seg_cases if c.revenue_leak)
            seg_ai_rec = sum(c.recovered_amount for c in seg_cases)
            seg_base_rec = seg_at_risk * (0.20 if seg in ["AT_RISK", "CHURNING"] else 0.28)

            if seg_at_risk > 0:
                chart_items.append(
                    RecoveryComparisonChartItem(
                        segment=seg.replace("_", " ").title(),
                        baseline_recovered_inr=round(seg_base_rec, 2),
                        ai_recovered_inr=round(seg_ai_rec, 2),
                        total_at_risk_inr=round(seg_at_risk, 2),
                    )
                )

        return DashboardMetricsResponse(
            total_revenue_at_risk=round(total_at_risk, 2),
            total_recovered_revenue=round(total_recovered, 2),
            overall_recovery_rate=round(recovery_rate, 2),
            net_roi_percent=round(net_roi, 2),
            baseline_recovery_rate=baseline_rate,
            recovery_uplift_inr=round(uplift_inr, 2),
            active_cases_count=active_count,
            escalated_cases_count=escalated_count,
            policy_interventions_count=blocked_count + escalated_count,
            comparison_chart=chart_items,
        )

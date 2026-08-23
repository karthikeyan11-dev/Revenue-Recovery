import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.analytics.baseline import BaselineSimulator
from app.analytics.metrics import RecoveryMetricsCalculator
from app.models.payment_failure import PaymentFailure
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.recovery_metrics import RecoveryMetricsRecord, StrategyType
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
            failures = self.db.query(PaymentFailure).limit(limit or 100).all()

        logger.info(f"Running AI Orchestrator simulation on {len(failures)} failures...")

        total_at_risk = 0.0
        total_recovered = 0.0
        total_cost = 0.0
        recovered_cases = 0
        escalated_cases = 0
        rejected_actions = 0

        segment_data: dict[str, dict[str, float]] = {}

        for fail in failures:
            amount = fail.transaction.amount
            total_at_risk += amount
            seg = (
                fail.transaction.customer.segment.value
                if fail.transaction and fail.transaction.customer
                else "REGULAR"
            )

            if seg not in segment_data:
                segment_data[seg] = {"at_risk": 0.0, "recovered": 0.0}
            segment_data[seg]["at_risk"] += amount

            case = self.recovery_service.process_single_failure_pipeline(fail, use_mock=use_mock)

            if case.status == CaseStatus.RECOVERED:
                total_recovered += case.recovered_amount
                total_cost += case.recovery_cost
                recovered_cases += 1
                segment_data[seg]["recovered"] += case.recovered_amount
            elif case.status == CaseStatus.ESCALATED:
                escalated_cases += 1
            elif case.status == CaseStatus.BLOCKED:
                rejected_actions += 1

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
            strategy_name="AI_ORCHESTRATOR",
            total_at_risk=total_at_risk,
            total_recovered=total_recovered,
            total_cost=total_cost,
            cases_count=len(failures),
            recovered_cases_count=recovered_cases,
            escalated_count=escalated_cases,
            rejected_count=rejected_actions,
        )

        # Persist snapshot to recovery_metrics table
        record = RecoveryMetricsRecord(
            id=f"met_ai_{uuid.uuid4().hex[:12]}",
            strategy_name=StrategyType.AI_ORCHESTRATOR,
            total_revenue_at_risk=metrics.total_revenue_at_risk,
            total_recovered_revenue=metrics.total_recovered_revenue,
            recovery_rate_percent=metrics.recovery_rate_percent,
            total_cost=metrics.total_cost,
            net_roi_percent=metrics.net_roi_percent,
            cases_count=metrics.cases_count,
            recovered_cases_count=metrics.recovered_cases_count,
            escalated_cases_count=metrics.escalated_cases_count,
            rejected_actions_count=metrics.rejected_actions_count,
            segment_breakdown=segment_breakdown,
            created_at=datetime.utcnow(),
        )
        self.recovery_repo.save_metrics_snapshot(record)

        return metrics

    def run_baseline_simulation(self, limit: int | None = None) -> StrategyMetrics:
        failures = self.db.query(PaymentFailure).limit(limit or 100).all()
        metrics, segment_breakdown = BaselineSimulator.run_benchmark(failures)

        # Persist snapshot to recovery_metrics table
        record = RecoveryMetricsRecord(
            id=f"met_base_{uuid.uuid4().hex[:12]}",
            strategy_name=StrategyType.BASELINE_RETRY_ONCE,
            total_revenue_at_risk=metrics.total_revenue_at_risk,
            total_recovered_revenue=metrics.total_recovered_revenue,
            recovery_rate_percent=metrics.recovery_rate_percent,
            total_cost=metrics.total_cost,
            net_roi_percent=metrics.net_roi_percent,
            cases_count=metrics.cases_count,
            recovered_cases_count=metrics.recovered_cases_count,
            escalated_cases_count=metrics.escalated_cases_count,
            rejected_actions_count=metrics.rejected_actions_count,
            segment_breakdown=segment_breakdown,
            created_at=datetime.utcnow(),
        )
        self.recovery_repo.save_metrics_snapshot(record)

        return metrics

    def get_dashboard_summary(self) -> DashboardMetricsResponse:
        ai_snapshot = self.recovery_repo.get_latest_metrics(StrategyType.AI_ORCHESTRATOR)
        base_snapshot = self.recovery_repo.get_latest_metrics(StrategyType.BASELINE_RETRY_ONCE)
        case_counts = self.recovery_repo.count_cases_by_status()

        # If no AI simulation run has been recorded in recovery_metrics yet, check DB cases
        if not ai_snapshot:
            cases = self.db.query(RecoveryCase).all()
            if not cases:
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
            # Reconstruct from cases if present
            total_at_risk = sum(c.revenue_leak.amount for c in cases if c.revenue_leak)
            total_recovered = sum(c.recovered_amount for c in cases)
            total_cost = sum(c.recovery_cost for c in cases)
            recovery_rate = (total_recovered / total_at_risk * 100.0) if total_at_risk > 0 else 0.0
            net_roi = (
                ((total_recovered - total_cost) / total_at_risk * 100.0)
                if total_at_risk > 0
                else 0.0
            )
            base_rate = base_snapshot.recovery_rate_percent if base_snapshot else 0.0
            base_recovered = base_snapshot.total_recovered_revenue if base_snapshot else 0.0
            uplift_inr = max(0.0, total_recovered - base_recovered)

            return DashboardMetricsResponse(
                total_revenue_at_risk=round(total_at_risk, 2),
                total_recovered_revenue=round(total_recovered, 2),
                overall_recovery_rate=round(recovery_rate, 2),
                net_roi_percent=round(net_roi, 2),
                baseline_recovery_rate=round(base_rate, 2),
                recovery_uplift_inr=round(uplift_inr, 2),
                active_cases_count=case_counts["open"] + case_counts["in_progress"],
                escalated_cases_count=case_counts["escalated"],
                policy_interventions_count=case_counts["blocked"] + case_counts["escalated"],
                comparison_chart=[],
            )

        # Genuinely read metrics from DB snapshots
        total_at_risk = ai_snapshot.total_revenue_at_risk
        total_recovered = ai_snapshot.total_recovered_revenue
        recovery_rate = ai_snapshot.recovery_rate_percent
        net_roi = ai_snapshot.net_roi_percent

        base_rate = base_snapshot.recovery_rate_percent if base_snapshot else 0.0
        base_recovered = base_snapshot.total_recovered_revenue if base_snapshot else 0.0
        uplift_inr = round(max(0.0, total_recovered - base_recovered), 2)

        # Build comparison chart from real persisted segment breakdowns
        ai_seg_map = {item["segment"]: item for item in (ai_snapshot.segment_breakdown or [])}
        base_seg_map = {
            item["segment"]: item
            for item in ((base_snapshot.segment_breakdown if base_snapshot else []) or [])
        }

        all_segments = list(dict.fromkeys(list(ai_seg_map.keys()) + list(base_seg_map.keys())))
        chart_items: list[RecoveryComparisonChartItem] = []

        for seg in all_segments:
            ai_item = ai_seg_map.get(seg, {})
            base_item = base_seg_map.get(seg, {})
            at_risk = ai_item.get("total_at_risk_inr") or base_item.get("total_at_risk_inr") or 0.0
            ai_rec = ai_item.get("recovered_inr", 0.0)
            base_rec = base_item.get("recovered_inr", 0.0)

            chart_items.append(
                RecoveryComparisonChartItem(
                    segment=seg.replace("_", " ").title(),
                    baseline_recovered_inr=round(base_rec, 2),
                    ai_recovered_inr=round(ai_rec, 2),
                    total_at_risk_inr=round(at_risk, 2),
                )
            )

        return DashboardMetricsResponse(
            total_revenue_at_risk=round(total_at_risk, 2),
            total_recovered_revenue=round(total_recovered, 2),
            overall_recovery_rate=round(recovery_rate, 2),
            net_roi_percent=round(net_roi, 2),
            baseline_recovery_rate=round(base_rate, 2),
            recovery_uplift_inr=uplift_inr,
            active_cases_count=case_counts["open"] + case_counts["in_progress"],
            escalated_cases_count=case_counts["escalated"],
            policy_interventions_count=case_counts["blocked"] + case_counts["escalated"],
            comparison_chart=chart_items,
        )

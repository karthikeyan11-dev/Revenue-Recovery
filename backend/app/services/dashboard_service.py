import logging

from sqlalchemy.orm import Session

from app.models.recovery_case import RecoveryCase
from app.models.recovery_metrics import StrategyType
from app.repositories.recovery import RecoveryRepository
from app.schemas.dashboard import DashboardMetricsResponse, RecoveryComparisonChartItem

logger = logging.getLogger("app.services.dashboard")


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.recovery_repo = RecoveryRepository(db)

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


# Compatibility alias
AnalyticsService = DashboardService

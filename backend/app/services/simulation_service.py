import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.analytics.baseline import BaselineSimulator
from app.analytics.metrics import RecoveryMetricsCalculator
from app.models.payment_failure import PaymentFailure
from app.models.recovery_case import CaseStatus
from app.models.recovery_metrics import RecoveryMetricsRecord, StrategyType
from app.repositories.recovery import RecoveryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.analyst import StrategyMetrics
from app.services.recovery_orchestrator import RecoveryOrchestratorService

logger = logging.getLogger("app.services.simulation")


class SimulationService:
    def __init__(self, db: Session):
        self.db = db
        self.recovery_repo = RecoveryRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.recovery_service = RecoveryOrchestratorService(db)

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

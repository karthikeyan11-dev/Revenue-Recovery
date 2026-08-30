from datetime import datetime
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.customer import Customer
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.promise_to_pay import PromiseStatus, PromiseToPay
from app.models.recovery_action import RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.recovery_metrics import RecoveryMetricsRecord, StrategyType
from app.models.revenue_leak import RevenueLeak
from app.repositories.base import BaseRepository


class RecoveryRepository(BaseRepository[RecoveryCase]):
    def __init__(self, db: Session):
        super().__init__(RecoveryCase, db)

    # Empirical Bayesian Statistics (Laplace Smoothing)
    @staticmethod
    def calculate_laplace_confidence(
        successes: int,
        total: int,
        prior_successes: int = 2,
        prior_total: int = 4,
    ) -> float:
        """
        Computes Laplace-smoothed empirical confidence score.
        Formula: (successes + prior_successes) / (total + prior_total)
        Default prior is 2 / 4 = 0.50 (neutral base rate under uncertainty).
        """
        return round(float(successes + prior_successes) / float(total + prior_total), 4)

    def get_empirical_failure_recovery_stats(
        self, failure_reason: FailureReason | str
    ) -> tuple[int, int]:
        """
        Executes real SQL aggregate query over past resolved cases matching the same failure_reason.
        Returns (successes, total_cases).
        """
        resolved_statuses = [
            CaseStatus.RECOVERED,
            CaseStatus.FAILED,
            CaseStatus.ESCALATED,
            CaseStatus.BLOCKED,
        ]

        res = (
            self.db.query(
                func.count(RecoveryCase.id).label("total"),
                func.count(case((RecoveryCase.status == CaseStatus.RECOVERED, 1))).label(
                    "successes"
                ),
            )
            .join(RevenueLeak, RecoveryCase.leak_id == RevenueLeak.id)
            .join(PaymentFailure, RevenueLeak.failure_id == PaymentFailure.id)
            .filter(PaymentFailure.failure_reason == failure_reason)
            .filter(RecoveryCase.status.in_(resolved_statuses))
            .first()
        )

        if not res or res.total is None or res.total == 0:
            return 0, 0
        return int(res.successes or 0), int(res.total or 0)

    # Alias for convenience
    get_empirical_failure_stats = get_empirical_failure_recovery_stats

    def get_empirical_customer_risk_stats(
        self, churn_risk: float = 0.50
    ) -> tuple[int, int]:
        """
        Executes real SQL aggregate query over past resolved cases.
        Returns (successes, total_cases).
        """
        resolved_statuses = [
            CaseStatus.RECOVERED,
            CaseStatus.FAILED,
            CaseStatus.ESCALATED,
            CaseStatus.BLOCKED,
        ]

        query = (
            self.db.query(
                func.count(RecoveryCase.id).label("total"),
                func.count(case((RecoveryCase.status == CaseStatus.RECOVERED, 1))).label(
                    "successes"
                ),
            )
            .filter(RecoveryCase.status.in_(resolved_statuses))
        )

        res = query.first()
        if not res or res.total is None or res.total == 0:
            return 0, 0
        return int(res.successes or 0), int(res.total or 0)

    def get_empirical_segment_recovery_stats(
        self, segment: Any = None
    ) -> tuple[int, int]:
        """Backwards compatibility alias for generic recovery stats."""
        return self.get_empirical_customer_risk_stats()

    # Revenue Leaks
    def create_leak(self, leak: RevenueLeak) -> RevenueLeak:
        self.db.add(leak)
        self.db.commit()
        return leak

    def get_all_leaks(self) -> list[RevenueLeak]:
        return self.db.query(RevenueLeak).all()

    # Recovery Cases
    def create_case(self, case: RecoveryCase) -> RecoveryCase:
        self.db.add(case)
        self.db.commit()
        return case

    def get_case_by_id(self, case_id: str) -> RecoveryCase | None:
        return (
            self.db.query(RecoveryCase)
            .options(
                joinedload(RecoveryCase.customer),
                joinedload(RecoveryCase.revenue_leak),
                joinedload(RecoveryCase.recovery_actions),
                joinedload(RecoveryCase.audit_logs),
            )
            .filter(RecoveryCase.id == case_id)
            .first()
        )

    def get_all_cases(
        self,
        limit: int = 100,
        offset: int = 0,
        status: CaseStatus | None = None,
        priority: str | None = None,
        search: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[RecoveryCase], int]:
        query = (
            self.db.query(RecoveryCase)
            .join(Customer, RecoveryCase.customer_id == Customer.id)
            .join(RevenueLeak, RecoveryCase.leak_id == RevenueLeak.id)
            .options(
                joinedload(RecoveryCase.customer),
                joinedload(RecoveryCase.revenue_leak),
                joinedload(RecoveryCase.recovery_actions),
                joinedload(RecoveryCase.promises_to_pay),
                joinedload(RecoveryCase.audit_logs),
            )
            .order_by(RecoveryCase.created_at.desc())
        )

        if status:
            query = query.filter(RecoveryCase.status == status)

        if search:
            s = f"%{search.strip()}%"
            query = query.filter(
                (RecoveryCase.id.ilike(s))
                | (Customer.name.ilike(s))
                | (Customer.email.ilike(s))
                | (RecoveryCase.customer_id.ilike(s))
            )

        if date_from:
            query = query.filter(RecoveryCase.created_at >= date_from)
        if date_to:
            query = query.filter(RecoveryCase.created_at <= date_to)

        if priority:
            p_upper = priority.strip().upper()
            if p_upper == "HIGH":
                query = query.filter(RevenueLeak.amount >= 20000.0)
            elif p_upper == "LOW":
                query = query.filter(RevenueLeak.amount < 5000.0)
            elif p_upper == "MEDIUM":
                query = query.filter(
                    (RevenueLeak.amount >= 5000.0) & (RevenueLeak.amount < 20000.0)
                )

        total = query.count()
        items = query.offset(offset).limit(limit).all()
        return items, total

    def list_cases(
        self,
        status: CaseStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        priority: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[RecoveryCase], int]:
        return self.get_all_cases(
            limit=limit,
            offset=offset,
            status=status,
            priority=priority,
            date_from=date_from,
            date_to=date_to,
        )

    def count_cases_by_status(self) -> dict:
        cases = self.db.query(RecoveryCase).all()
        return {
            "total": len(cases),
            "open": sum(1 for c in cases if c.status == CaseStatus.OPEN),
            "in_progress": sum(1 for c in cases if c.status == CaseStatus.IN_PROGRESS),
            "recovered": sum(1 for c in cases if c.status == CaseStatus.RECOVERED),
            "failed": sum(1 for c in cases if c.status == CaseStatus.FAILED),
            "escalated": sum(1 for c in cases if c.status == CaseStatus.ESCALATED),
            "blocked": sum(1 for c in cases if c.status == CaseStatus.BLOCKED),
        }

    # Recovery Actions
    def create_action(self, action: RecoveryAction) -> RecoveryAction:
        self.db.add(action)
        self.db.commit()
        return action

    # Communication Events
    def create_communication_event(self, event: CommunicationEvent) -> CommunicationEvent:
        self.db.add(event)
        self.db.commit()
        return event

    # Audit Logs
    def create_audit_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.commit()
        return log

    def get_audit_logs_for_case(self, case_id: str) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.case_id == case_id)
            .order_by(AuditLog.timestamp.asc())
            .all()
        )

    def get_recent_activities(self, limit: int = 50) -> list[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()

    # Promise-to-Pay Records
    def create_promise_to_pay(self, promise: PromiseToPay) -> PromiseToPay:
        self.db.add(promise)
        self.db.commit()
        return promise

    def get_promise_by_id(self, promise_id: str) -> PromiseToPay | None:
        return (
            self.db.query(PromiseToPay)
            .options(
                joinedload(PromiseToPay.recovery_case).joinedload(RecoveryCase.customer),
                joinedload(PromiseToPay.recovery_case).joinedload(RecoveryCase.revenue_leak),
            )
            .filter(PromiseToPay.id == promise_id)
            .first()
        )

    def get_promises_for_case(self, case_id: str) -> list[PromiseToPay]:
        return (
            self.db.query(PromiseToPay)
            .filter(PromiseToPay.case_id == case_id)
            .order_by(PromiseToPay.created_at.desc())
            .all()
        )

    def get_all_promises(
        self,
        limit: int = 100,
        offset: int = 0,
        status: PromiseStatus | None = None,
    ) -> list[PromiseToPay]:
        query = (
            self.db.query(PromiseToPay)
            .options(
                joinedload(PromiseToPay.recovery_case).joinedload(RecoveryCase.customer),
                joinedload(PromiseToPay.recovery_case).joinedload(RecoveryCase.revenue_leak),
            )
            .order_by(PromiseToPay.created_at.desc())
        )
        if status:
            query = query.filter(PromiseToPay.status == status)
        return query.offset(offset).limit(limit).all()

    def count_promises_by_status(self) -> dict:
        promises = self.db.query(PromiseToPay).all()
        return {
            "total": len(promises),
            "pending": sum(1 for p in promises if p.status == PromiseStatus.PENDING),
            "kept": sum(1 for p in promises if p.status == PromiseStatus.KEPT),
            "broken": sum(1 for p in promises if p.status == PromiseStatus.BROKEN),
        }

    # Recovery Metrics Snapshots
    def save_metrics_snapshot(self, record: RecoveryMetricsRecord) -> RecoveryMetricsRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_metrics(self, strategy_name: StrategyType | str) -> RecoveryMetricsRecord | None:
        return (
            self.db.query(RecoveryMetricsRecord)
            .filter(RecoveryMetricsRecord.strategy_name == strategy_name)
            .order_by(RecoveryMetricsRecord.created_at.desc())
            .first()
        )

from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.customer import Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.promise_to_pay import PromiseStatus, PromiseToPay
from app.models.recovery_action import RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.recovery_metrics import RecoveryMetricsRecord, StrategyType
from app.models.revenue_leak import RevenueLeak


class RecoveryRepository:
    def __init__(self, db: Session):
        self.db = db

    # Empirical Statistical Aggregates (Laplace-Smoothed Confidence Engine)
    @staticmethod
    def calculate_laplace_confidence(
        successes: int,
        total: int,
        prior_successes: int = 2,
        prior_total: int = 4,
    ) -> float:
        """
        Computes empirical confidence with Laplace smoothing (weak Bayesian prior):
        confidence = (successes + 2) / (total + 4)
        """
        return round((successes + prior_successes) / (total + prior_total), 4)

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

    def get_empirical_segment_recovery_stats(
        self, segment: CustomerSegment | str
    ) -> tuple[int, int]:
        """
        Executes real SQL aggregate query over past resolved cases for customers in the same segment.
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
            .join(Customer, RecoveryCase.customer_id == Customer.id)
            .filter(Customer.segment == segment)
            .filter(RecoveryCase.status.in_(resolved_statuses))
            .first()
        )

        if not res or res.total is None or res.total == 0:
            return 0, 0
        return int(res.successes or 0), int(res.total or 0)

    # Revenue Leaks
    def create_leak(self, leak: RevenueLeak) -> RevenueLeak:
        self.db.add(leak)
        self.db.commit()
        self.db.refresh(leak)
        return leak

    def get_all_leaks(self) -> list[RevenueLeak]:
        return self.db.query(RevenueLeak).all()

    # Recovery Cases
    def create_case(self, case: RecoveryCase) -> RecoveryCase:
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
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
        self, limit: int = 100, offset: int = 0, status: CaseStatus | None = None
    ) -> list[RecoveryCase]:
        query = (
            self.db.query(RecoveryCase)
            .options(
                joinedload(RecoveryCase.customer),
                joinedload(RecoveryCase.revenue_leak),
            )
            .order_by(RecoveryCase.created_at.desc())
        )
        if status:
            query = query.filter(RecoveryCase.status == status)
        return query.offset(offset).limit(limit).all()

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
        self.db.refresh(action)
        return action

    # Communication Events
    def create_communication_event(self, event: CommunicationEvent) -> CommunicationEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    # Audit Logs
    def create_audit_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
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
        self.db.refresh(promise)
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

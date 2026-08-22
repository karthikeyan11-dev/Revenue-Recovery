from sqlalchemy.orm import Session, joinedload

from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.recovery_action import RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import RevenueLeak


class RecoveryRepository:
    def __init__(self, db: Session):
        self.db = db

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

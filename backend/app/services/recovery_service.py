import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.executor.executor import ActionExecutor
from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.payment_failure import PaymentFailure
from app.models.recovery_action import ActionType, PolicyDecision, RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.policy.engine import PolicyEngine
from app.repositories.recovery_repository import RecoveryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.cases import (
    CaseActionItem,
    CasesListResponse,
    CaseTimelineItem,
    RecoveryCaseDetail,
    RecoveryCaseSummary,
)
from app.schemas.strategist import ProposedRecoveryAction

logger = logging.getLogger("app.services.recovery")


class RecoveryService:
    def __init__(self, db: Session):
        self.db = db
        self.recovery_repo = RecoveryRepository(db)
        self.transaction_repo = TransactionRepository(db)

    def list_cases(
        self,
        limit: int = 100,
        offset: int = 0,
        status: CaseStatus | None = None,
    ) -> CasesListResponse:
        cases = self.recovery_repo.get_all_cases(limit=limit, offset=offset, status=status)
        counts = self.recovery_repo.count_cases_by_status()

        summaries = [
            RecoveryCaseSummary(
                id=c.id,
                customer_id=c.customer_id,
                customer_name=c.customer.name if c.customer else "Unknown",
                customer_email=c.customer.email if c.customer else "unknown@example.com",
                customer_segment=c.customer.segment if c.customer else "REGULAR",
                leak_type=(
                    c.revenue_leak.leak_type if c.revenue_leak else LeakType.TRANSACTION_FAILURE
                ),
                leak_amount=c.revenue_leak.amount if c.revenue_leak else 0.0,
                recoverability_score=c.revenue_leak.recoverability_score if c.revenue_leak else 0.5,
                status=c.status,
                recovered_amount=c.recovered_amount,
                recovery_cost=c.recovery_cost,
                created_at=c.created_at,
                resolved_at=c.resolved_at,
            )
            for c in cases
        ]

        return CasesListResponse(
            items=summaries,
            total=counts["total"],
            open_count=counts["open"] + counts["in_progress"],
            recovered_count=counts["recovered"],
            escalated_count=counts["escalated"],
            failed_count=counts["failed"] + counts["blocked"],
        )

    def get_case_detail(self, case_id: str) -> RecoveryCaseDetail | None:
        case = self.recovery_repo.get_case_by_id(case_id)
        if not case:
            return None

        actions = [
            CaseActionItem(
                id=a.id,
                proposed_action=a.proposed_action,
                policy_decision=a.policy_decision,
                policy_reasoning=a.policy_reasoning,
                outcome=a.outcome,
                incentive_percent=a.incentive_percent,
                created_at=a.created_at,
            )
            for a in case.recovery_actions
        ]

        timeline = [
            CaseTimelineItem(
                id=log.id,
                agent=log.agent,
                step_name=log.step_name,
                input_summary=log.input_summary,
                output_summary=log.output_summary,
                decision=log.decision,
                confidence=log.confidence,
                timestamp=log.timestamp,
            )
            for log in case.audit_logs
        ]

        return RecoveryCaseDetail(
            id=case.id,
            customer_id=case.customer_id,
            customer_name=case.customer.name if case.customer else "Unknown",
            customer_email=case.customer.email if case.customer else "unknown@example.com",
            customer_segment=case.customer.segment if case.customer else "REGULAR",
            leak_type=(
                case.revenue_leak.leak_type if case.revenue_leak else LeakType.TRANSACTION_FAILURE
            ),
            leak_amount=case.revenue_leak.amount if case.revenue_leak else 0.0,
            recoverability_score=(
                case.revenue_leak.recoverability_score if case.revenue_leak else 0.5
            ),
            status=case.status,
            recovered_amount=case.recovered_amount,
            recovery_cost=case.recovery_cost,
            created_at=case.created_at,
            resolved_at=case.resolved_at,
            actions=actions,
            timeline=timeline,
        )

    def process_single_failure_pipeline(
        self,
        failure: PaymentFailure,
        use_mock: bool = True,
    ) -> RecoveryCase:
        """
        Executes the Detective -> Intel -> Strategist -> Policy -> Executor pipeline for one failure.
        """
        tx = failure.transaction
        customer = tx.customer

        # 1. Detective Detection
        leak_id = f"leak_{uuid.uuid4().hex[:14]}"
        recoverability = (
            0.85
            if failure.failure_reason.value
            in ["INSUFFICIENT_FUNDS", "NETWORK_ERROR", "USER_DROPOFF"]
            else 0.50
        )
        leak = RevenueLeak(
            id=leak_id,
            failure_id=failure.id,
            leak_type=LeakType.TRANSACTION_FAILURE,
            amount=tx.amount,
            confidence=0.92,
            recoverability_score=recoverability,
            reasoning=f"Detected payment drop from {failure.failure_reason.value}. Recoverability score: {recoverability:.2f}",
        )
        self.recovery_repo.create_leak(leak)

        # Create Case
        case_id = f"case_{uuid.uuid4().hex[:14]}"
        case = RecoveryCase(
            id=case_id,
            leak_id=leak.id,
            customer_id=customer.id,
            status=CaseStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
        )
        self.recovery_repo.create_case(case)

        # Audit Log: Detective
        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Revenue Detective",
                step_name="LEAK_DETECTION",
                input_summary=f"Txn: {tx.id}, Amount: ₹{tx.amount:,.2f}, Reason: {failure.failure_reason.value}",
                output_summary=f"Identified {leak.leak_type.value}, Recoverability: {leak.recoverability_score:.2f}",
                decision="LEAK_CONFIRMED",
                confidence=0.92,
            )
        )

        # 2. Customer Intelligence
        churn_risk = customer.churn_probability
        pref_channel = customer.preferred_channel.value
        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Customer Intelligence",
                step_name="PROFILE_ANALYSIS",
                input_summary=f"Customer: {customer.name}, Segment: {customer.segment.value}, LTV: ₹{customer.ltv:,.2f}",
                output_summary=f"Churn Risk: {churn_risk:.0%}, Channel: {pref_channel}, Recovery Prob: {recoverability:.0%}",
                decision="PROFILE_READY",
                confidence=0.88,
            )
        )

        # 3. Recovery Strategist
        if failure.failure_reason.value == "INSUFFICIENT_FUNDS":
            proposed_action = ProposedRecoveryAction(
                action_type=ActionType.RETRY,
                retry_delay_hours=12,
                reasoning="Soft failure due to insufficient balance. Schedule retry in 12h after typical banking top-up window.",
            )
        elif customer.segment.value in ["HIGH_VALUE", "LOYAL"]:
            proposed_action = ProposedRecoveryAction(
                action_type=ActionType.SEND_WHATSAPP,
                incentive_percent=5.0,
                channel="WHATSAPP",
                reasoning="High-value customer failed on cart. Send personalized WhatsApp recovery link with 5% goodwill discount.",
            )
        elif customer.segment.value in ["AT_RISK", "CHURNING"]:
            proposed_action = ProposedRecoveryAction(
                action_type=ActionType.OFFER_INCENTIVE,
                incentive_percent=10.0,
                channel="WHATSAPP",
                reasoning="At-risk customer at imminent churn danger. Provide bounded 10% instant re-engagement discount.",
            )
        elif failure.failure_reason.value == "EXPIRED_CARD":
            proposed_action = ProposedRecoveryAction(
                action_type=ActionType.SEND_EMAIL,
                channel="EMAIL",
                reasoning="Card expired. Automated retry will fail. Send updated payment method link via email.",
            )
        else:
            proposed_action = ProposedRecoveryAction(
                action_type=ActionType.RETRY,
                retry_delay_hours=2,
                reasoning="Network or transient failure. Fast retry scheduled.",
            )

        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Recovery Strategist",
                step_name="STRATEGY_PROPOSAL",
                input_summary=f"Leak: ₹{tx.amount:,.2f}, Profile: {customer.segment.value}, Churn: {churn_risk:.0%}",
                output_summary=f"Proposed: {proposed_action.action_type.value} (Discount: {proposed_action.incentive_percent}%)",
                decision=proposed_action.action_type.value,
                confidence=0.85,
            )
        )

        # 4. Policy Engine Evaluation (Strict Deterministic Guard)
        policy_res = PolicyEngine.evaluate(
            proposal=proposed_action,
            amount=tx.amount,
            previous_attempts=failure.attempt_number,
            customer_churn_risk=churn_risk,
        )

        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Policy Engine",
                step_name="POLICY_GATE",
                input_summary=f"Proposed: {proposed_action.action_type.value}, Rule check against limits",
                output_summary=policy_res.reasoning,
                decision=policy_res.decision.value,
                confidence=1.0,
            )
        )

        # Record Action in DB
        action_record = RecoveryAction(
            id=f"act_{uuid.uuid4().hex[:14]}",
            case_id=case.id,
            proposed_action=proposed_action.action_type,
            policy_decision=policy_res.decision,
            policy_reasoning=policy_res.reasoning,
            incentive_percent=proposed_action.incentive_percent,
            retry_delay_hours=proposed_action.retry_delay_hours,
        )

        # 5. Execution Dispatch
        exec_res = ActionExecutor.execute(
            action_type=proposed_action.action_type,
            policy_decision=policy_res.decision,
            amount=tx.amount,
            failure_reason=failure.failure_reason,
            attempt_number=failure.attempt_number,
            incentive_percent=proposed_action.incentive_percent,
            retry_delay_hours=proposed_action.retry_delay_hours,
            channel=proposed_action.channel,
            customer_contact=customer.email,
        )

        action_record.outcome = exec_res.outcome
        action_record.execution_details = exec_res.details
        action_record.executed_at = datetime.utcnow()
        self.recovery_repo.create_action(action_record)

        # Record Communication Event if triggered
        if exec_res.communication_event_data:
            c_data = exec_res.communication_event_data
            self.recovery_repo.create_communication_event(
                CommunicationEvent(
                    id=f"comm_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    channel=c_data["channel"],
                    recipient=c_data["recipient"],
                    message_content=c_data["message_content"],
                    simulated_response=c_data["simulated_response"],
                    responded_at=datetime.utcnow(),
                )
            )

        # Update Case Status
        if exec_res.recovered:
            case.status = CaseStatus.RECOVERED
            case.recovered_amount = tx.amount
            case.recovery_cost = exec_res.cost
            case.resolved_at = datetime.utcnow()
        elif policy_res.decision == PolicyDecision.ESCALATED:
            case.status = CaseStatus.ESCALATED
        elif policy_res.decision == PolicyDecision.REJECTED:
            case.status = CaseStatus.BLOCKED
        else:
            case.status = CaseStatus.FAILED

        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Action Executor",
                step_name="DISPATCH_OUTCOME",
                input_summary=f"Action: {proposed_action.action_type.value}, Policy: {policy_res.decision.value}",
                output_summary=f"Result: {exec_res.outcome.value} | {exec_res.details} | Cost: ₹{exec_res.cost:.2f}",
                decision="RECOVERED" if exec_res.recovered else "FAILED",
                confidence=1.0,
            )
        )

        self.db.commit()
        return case

import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.agents.graph import RecoveryAgentState, recovery_graph
from app.agents.recovery_analyst import RecoveryAnalystAgent
from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.payment_failure import PaymentFailure
from app.models.promise_to_pay import PromiseStatus, PromiseToPay
from app.models.recovery_action import ActionType, PolicyDecision, RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.repositories.recovery import RecoveryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.recovery import (
    CaseActionItem,
    CasesListResponse,
    CaseTimelineItem,
    RecoveryCaseDetail,
    RecoveryCaseSummary,
)
from app.schemas.promise import PromiseToPaySummary

logger = logging.getLogger("app.services.recovery_orchestrator")


class RecoveryOrchestratorService:
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

        summaries = []
        for c in cases:
            strat_log = next(
                (log for log in c.audit_logs if log.agent == "Recovery Strategist"), None
            )
            precedent_count = (
                strat_log.precedent_sample_size
                if strat_log and strat_log.precedent_sample_size is not None
                else 0
            )

            has_insufficient_escalation = any(
                (
                    act.policy_decision == PolicyDecision.ESCALATED
                    and "precedent" in (act.policy_reasoning or "").lower()
                )
                for act in c.recovery_actions
            ) or (
                strat_log is not None
                and strat_log.precedent_sample_size is not None
                and strat_log.precedent_sample_size < 3
            )

            ptp = c.promises_to_pay[-1] if c.promises_to_pay else None
            promise_status = ptp.status.value if ptp else None

            summaries.append(
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
                    recoverability_score=(
                        c.revenue_leak.recoverability_score if c.revenue_leak else 0.5
                    ),
                    status=c.status,
                    recovered_amount=c.recovered_amount,
                    recovery_cost=c.recovery_cost,
                    has_sufficient_precedent=not has_insufficient_escalation,
                    precedent_count=precedent_count,
                    promise_status=promise_status,
                    created_at=c.created_at,
                    resolved_at=c.resolved_at,
                )
            )

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
                empirical_confidence=(
                    log.empirical_confidence
                    if log.empirical_confidence is not None
                    else log.confidence
                ),
                llm_stated_confidence=log.llm_stated_confidence,
                precedent_sample_size=log.precedent_sample_size or 0,
                timestamp=log.timestamp,
            )
            for log in case.audit_logs
        ]

        strat_log = next(
            (log for log in case.audit_logs if log.agent == "Recovery Strategist"), None
        )
        precedent_count = (
            strat_log.precedent_sample_size
            if strat_log and strat_log.precedent_sample_size is not None
            else 0
        )

        has_insufficient_escalation = any(
            (
                act.policy_decision == PolicyDecision.ESCALATED
                and "precedent" in (act.policy_reasoning or "").lower()
            )
            for act in case.recovery_actions
        ) or (
            strat_log is not None
            and strat_log.precedent_sample_size is not None
            and strat_log.precedent_sample_size < 3
        )

        ptp = case.promises_to_pay[-1] if case.promises_to_pay else None
        promise_status = ptp.status.value if ptp else None

        promises = [
            PromiseToPaySummary(
                id=p.id,
                case_id=p.case_id,
                customer_id=case.customer_id,
                customer_name=case.customer.name if case.customer else "Unknown",
                customer_email=case.customer.email if case.customer else "unknown@example.com",
                customer_segment=(
                    case.customer.segment.value
                    if case.customer and case.customer.segment
                    else "REGULAR"
                ),
                committed_amount=p.committed_amount,
                committed_date=p.committed_date,
                status=p.status,
                follow_up_count=p.follow_up_count,
                created_at=p.created_at,
                resolved_at=p.resolved_at,
            )
            for p in case.promises_to_pay
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
            has_sufficient_precedent=not has_insufficient_escalation,
            precedent_count=precedent_count,
            promise_status=promise_status,
            created_at=case.created_at,
            resolved_at=case.resolved_at,
            actions=actions,
            timeline=timeline,
            promises=promises,
        )

    def process_single_failure_pipeline(
        self,
        failure: PaymentFailure,
        use_mock: bool = True,
    ) -> RecoveryCase:
        """
        Executes the compiled LangGraph workflow (Detective -> Intel -> Strategist -> Policy -> Executor)
        and persists the resulting domain models and audit logs.
        """
        tx = failure.transaction
        customer = tx.customer

        # 1. Execute the full multi-agent LangGraph workflow
        initial_state: RecoveryAgentState = {
            "failure": failure,
            "db": self.db,
            "detective_output": None,
            "intel_output": None,
            "proposed_action": None,
            "policy_decision": None,
            "policy_reasoning": None,
            "execution_outcome": None,
            "recovered": False,
            "recovered_amount": 0.0,
            "cost": 0.0,
            "details": "",
            "communication_event_data": None,
        }

        final_state = recovery_graph.invoke(initial_state)

        det_out = final_state["detective_output"]
        intel_out = final_state["intel_output"]
        strat_out = final_state["proposed_action"]
        policy_decision = final_state["policy_decision"]
        policy_reasoning = final_state["policy_reasoning"]
        exec_outcome = final_state["execution_outcome"]
        recovered = final_state["recovered"]
        recovered_amount = final_state["recovered_amount"]
        cost = final_state["cost"]
        details = final_state["details"]
        comm_data = final_state["communication_event_data"]

        # 2. Persist Revenue Leak
        leak_id = f"leak_{uuid.uuid4().hex[:14]}"
        leak = RevenueLeak(
            id=leak_id,
            failure_id=failure.id,
            leak_type=det_out.leak_type if det_out else LeakType.TRANSACTION_FAILURE,
            amount=det_out.amount if det_out else tx.amount,
            confidence=det_out.confidence if det_out else 0.50,
            recoverability_score=det_out.recoverability_score if det_out else 0.50,
            reasoning=(
                det_out.reasoning
                if det_out
                else f"Detected leak from {failure.failure_reason.value}"
            ),
        )
        self.recovery_repo.create_leak(leak)

        # 3. Persist Recovery Case
        case_id = f"case_{uuid.uuid4().hex[:14]}"
        case = RecoveryCase(
            id=case_id,
            leak_id=leak.id,
            customer_id=customer.id,
            status=CaseStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
        )
        self.recovery_repo.create_case(case)

        # 4. Persist Audit Logs
        # Detective Audit Log
        if det_out:
            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Revenue Detective",
                    step_name="LEAK_DETECTION",
                    input_summary=f"Txn: {tx.id}, Amount: ₹{tx.amount:,.2f}, Reason: {failure.failure_reason.value}",
                    output_summary=f"Identified {det_out.leak_type.value}, Recoverability: {det_out.recoverability_score:.2f} (Empirical Precedent: n={det_out.precedent_sample_size})",
                    decision="LEAK_CONFIRMED",
                    confidence=det_out.confidence,
                    empirical_confidence=det_out.confidence,
                    llm_stated_confidence=det_out.llm_stated_confidence,
                    precedent_sample_size=det_out.precedent_sample_size,
                )
            )

        # Customer Intelligence Audit Log
        if intel_out:
            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Customer Intelligence",
                    step_name="PROFILE_ANALYSIS",
                    input_summary=f"Customer: {customer.name}, Segment: {intel_out.segment.value}, LTV: ₹{intel_out.ltv:,.2f}",
                    output_summary=f"Churn Risk: {intel_out.churn_probability:.0%}, Channel: {intel_out.preferred_channel.value}, Recovery Prob: {intel_out.recovery_probability:.0%} (Empirical Precedent: n={intel_out.precedent_sample_size})",
                    decision="PROFILE_READY",
                    confidence=intel_out.confidence,
                    empirical_confidence=intel_out.confidence,
                    llm_stated_confidence=intel_out.llm_stated_confidence,
                    precedent_sample_size=intel_out.precedent_sample_size,
                )
            )

        # Recovery Strategist Audit Log
        if strat_out:
            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Recovery Strategist",
                    step_name="STRATEGY_PROPOSAL",
                    input_summary=f"Leak: ₹{tx.amount:,.2f}, Profile: {intel_out.segment.value if intel_out else 'REGULAR'}, Precedents: n={strat_out.retrieved_precedent_count} (Insufficient: {strat_out.insufficient_precedent})",
                    output_summary=f"Proposed: {strat_out.action_type.value} (Discount: {strat_out.incentive_percent}%), Empirical Conf: {strat_out.confidence:.4f}",
                    decision=strat_out.action_type.value,
                    confidence=strat_out.confidence,
                    empirical_confidence=strat_out.confidence,
                    llm_stated_confidence=strat_out.llm_stated_confidence,
                    precedent_sample_size=strat_out.retrieved_precedent_count,
                )
            )

        # Policy Engine Audit Log
        if policy_decision:
            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Policy Engine",
                    step_name="POLICY_GATE",
                    input_summary=f"Proposed: {strat_out.action_type.value if strat_out else 'UNKNOWN'}, Limits check",
                    output_summary=policy_reasoning or "Evaluated",
                    decision=policy_decision.value,
                    confidence=1.0,
                )
            )

        # 5. Persist Action Record
        action_record = RecoveryAction(
            id=f"act_{uuid.uuid4().hex[:14]}",
            case_id=case.id,
            proposed_action=strat_out.action_type if strat_out else ActionType.RETRY,
            policy_decision=policy_decision or PolicyDecision.APPROVED,
            policy_reasoning=policy_reasoning or "",
            incentive_percent=strat_out.incentive_percent if strat_out else 0.0,
            retry_delay_hours=strat_out.retry_delay_hours if strat_out else 0,
            outcome=exec_outcome,
            execution_details=details,
            executed_at=datetime.utcnow(),
        )
        self.recovery_repo.create_action(action_record)

        # 6. Persist Communication Event if triggered
        if comm_data:
            self.recovery_repo.create_communication_event(
                CommunicationEvent(
                    id=f"comm_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    channel=comm_data["channel"],
                    recipient=comm_data["recipient"],
                    message_content=comm_data["message_content"],
                    simulated_response=comm_data["simulated_response"],
                    responded_at=datetime.utcnow(),
                )
            )

        # 6.5 Persist Promise-to-Pay record if interactive outreach dispatched
        if (
            policy_decision == PolicyDecision.APPROVED
            and strat_out
            and strat_out.action_type
            in [
                ActionType.SEND_WHATSAPP,
                ActionType.SEND_PAYMENT_LINK,
                ActionType.SEND_EMAIL,
                ActionType.OFFER_INCENTIVE,
            ]
        ):
            promise_status = PromiseStatus.KEPT if recovered else PromiseStatus.PENDING
            promise_rec = PromiseToPay(
                id=f"ptp_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                committed_amount=leak.amount,
                committed_date=datetime.utcnow() + timedelta(days=2),
                status=promise_status,
                follow_up_count=0,
                created_at=datetime.utcnow(),
                resolved_at=datetime.utcnow() if recovered else None,
            )
            self.recovery_repo.create_promise_to_pay(promise_rec)

        # 7. Update Final Case Status
        if recovered:
            case.status = CaseStatus.RECOVERED
            case.recovered_amount = recovered_amount
            case.recovery_cost = cost
            case.resolved_at = datetime.utcnow()
        elif policy_decision == PolicyDecision.ESCALATED:
            case.status = CaseStatus.ESCALATED
        elif policy_decision == PolicyDecision.REJECTED:
            case.status = CaseStatus.BLOCKED
        else:
            case.status = CaseStatus.FAILED

        # Action Executor Audit Log
        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Action Executor",
                step_name="DISPATCH_OUTCOME",
                input_summary=f"Action: {strat_out.action_type.value if strat_out else 'UNKNOWN'}, Policy: {policy_decision.value if policy_decision else 'APPROVED'}",
                output_summary=f"Result: {exec_outcome.value if exec_outcome else 'FAILED'} | {details} | Cost: ₹{cost:.2f}",
                decision="RECOVERED" if recovered else "FAILED",
                confidence=1.0,
            )
        )

        # 8. Recovery Analyst writes resolved case back into ChromaDB recovery_playbook
        try:
            RecoveryAnalystAgent.write_back_resolved_case(
                case_id=case.id,
                segment=customer.segment.value if customer.segment else "REGULAR",
                failure_reason=failure.failure_reason.value,
                action_taken=strat_out.action_type.value if strat_out else "RETRY",
                channel=strat_out.channel if strat_out else None,
                outcome=case.status.value,
                recovered_amount=recovered_amount if recovered else 0.0,
            )
        except Exception as e:
            logger.error(f"Failed to write back case {case.id} to recovery playbook: {e}")

        self.db.commit()
        return case


# Compatibility alias
RecoveryService = RecoveryOrchestratorService

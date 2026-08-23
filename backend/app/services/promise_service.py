import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.recovery_analyst import RecoveryAnalystAgent
from app.agents.recovery_strategist import RecoveryStrategistAgent
from app.agents.revenue_detective import RevenueDetectiveAgent
from app.executor.executor import ActionExecutor
from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.payment_failure import PaymentFailure
from app.models.promise_to_pay import PromiseStatus, PromiseToPay
from app.models.recovery_action import PolicyDecision, RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.policy.engine import PolicyEngine
from app.policy.rules import MAX_PROMISE_FOLLOWUPS, RULE_MAX_PROMISE_FOLLOWUPS
from app.repositories.recovery_repository import RecoveryRepository
from app.schemas.promise import PromiseListResponse, PromiseToPaySummary

logger = logging.getLogger("app.services.promise")


class PromiseTrackerService:
    def __init__(self, db: Session):
        self.db = db
        self.recovery_repo = RecoveryRepository(db)

    def create_promise(
        self,
        case_id: str,
        committed_amount: float,
        days_to_pay: int = 2,
    ) -> PromiseToPay:
        """
        Creates a new Promise-to-Pay record in PENDING status for an interactive outreach case.
        """
        promise = PromiseToPay(
            id=f"ptp_{uuid.uuid4().hex[:14]}",
            case_id=case_id,
            committed_amount=committed_amount,
            committed_date=datetime.utcnow() + timedelta(days=days_to_pay),
            status=PromiseStatus.PENDING,
            follow_up_count=0,
            created_at=datetime.utcnow(),
        )
        saved = self.recovery_repo.create_promise_to_pay(promise)
        logger.info(
            f"[PromiseTracker] Created PENDING promise {saved.id} for Case {case_id} (Amount: ₹{committed_amount:,.2f})"
        )
        return saved

    def evaluate_promise(
        self,
        promise_id: str,
        is_paid: bool,
    ) -> tuple[PromiseToPay, RecoveryCase | None]:
        """
        Evaluates a promise as KEPT or BROKEN.
        - If KEPT: marks recovered and completes case.
        - If BROKEN:
            - If follow_up_count == 0: triggers exactly ONE automated follow-up loop through Strategist + Policy + Executor.
            - If follow_up_count >= 1: ENFORCES STOPPING RULE (mandatory human escalation, halts automated execution).
        """
        promise = self.recovery_repo.get_promise_by_id(promise_id)
        if not promise:
            raise ValueError(f"Promise-to-Pay with id '{promise_id}' not found.")

        case = promise.recovery_case
        customer = case.customer
        leak = case.revenue_leak
        failure: PaymentFailure = leak.payment_failure

        if is_paid:
            # 1. Promise KEPT
            promise.status = PromiseStatus.KEPT
            promise.resolved_at = datetime.utcnow()

            case.status = CaseStatus.RECOVERED
            case.recovered_amount = promise.committed_amount
            case.resolved_at = datetime.utcnow()

            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Promise Tracker",
                    step_name="PROMISE_RESOLUTION",
                    input_summary=f"Promise {promise.id} evaluated (Payment status check)",
                    output_summary=f"Customer kept payment promise. Successfully recovered ₹{promise.committed_amount:,.2f}",
                    decision="PROMISE_KEPT",
                    confidence=1.0,
                    empirical_confidence=1.0,
                )
            )

            # Write-back to ChromaDB playbook
            try:
                RecoveryAnalystAgent.write_back_resolved_case(
                    case_id=case.id,
                    segment=customer.segment.value if customer.segment else "REGULAR",
                    failure_reason=failure.failure_reason.value if failure else "UNKNOWN",
                    action_taken="PROMISE_TO_PAY",
                    channel=(
                        customer.preferred_channel.value
                        if customer.preferred_channel
                        else "WHATSAPP"
                    ),
                    outcome="SUCCESS",
                    recovered_amount=promise.committed_amount,
                )
            except Exception as e:
                logger.error(f"Failed to write back kept promise to ChromaDB: {e}")

            self.db.commit()
            logger.info(
                f"[PromiseTracker] Promise {promise.id} KEPT. Case {case.id} marked RECOVERED."
            )
            return promise, case

        # 2. Promise BROKEN
        promise.status = PromiseStatus.BROKEN
        promise.resolved_at = datetime.utcnow()

        logger.warning(
            f"[PromiseTracker] Promise {promise.id} BROKEN (Case {case.id}). Current follow_ups: {promise.follow_up_count}"
        )

        # Check Stopping Rule: If already had 1 follow-up, MUST escalate to human review immediately
        if promise.follow_up_count >= MAX_PROMISE_FOLLOWUPS:
            case.status = CaseStatus.ESCALATED
            case.resolved_at = datetime.utcnow()

            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Policy Engine",
                    step_name="STOPPING_RULE_ENFORCEMENT",
                    input_summary=f"Promise {promise.id} broke again after {promise.follow_up_count} follow-up(s)",
                    output_summary=f"Stopping rule enforced ({RULE_MAX_PROMISE_FOLLOWUPS}): Max {MAX_PROMISE_FOLLOWUPS} automated follow-up allowed. Mandatory human escalation.",
                    decision="ESCALATED",
                    confidence=1.0,
                    empirical_confidence=1.0,
                )
            )

            self.db.commit()
            logger.warning(
                f"[PromiseTracker] STOPPING RULE ENFORCED for Case {case.id}. Escalated to human queue."
            )
            return promise, case

        # 3. First Break: Execute exactly ONE bounded follow-up via Strategist + Policy + Executor
        promise.follow_up_count += 1
        logger.info(
            f"[PromiseTracker] Initiating Follow-Up #{promise.follow_up_count} for Case {case.id}"
        )

        # Detective & Customer Intelligence fresh profile
        det_out = RevenueDetectiveAgent.analyze(failure, db=self.db)
        intel_out = CustomerIntelligenceAgent.profile(customer, db=self.db)

        # Recovery Strategist RAG reasoning & empirical confidence
        strat_out = RecoveryStrategistAgent.propose_action(
            detective_output=det_out,
            intel_output=intel_out,
            failure_reason=failure.failure_reason.value if failure else None,
        )

        # Policy Engine Gate (with previous_promise_followups=0 for this first follow-up)
        policy_res = PolicyEngine.evaluate(
            proposal=strat_out,
            amount=leak.amount,
            previous_attempts=failure.attempt_number + 1,
            customer_churn_risk=intel_out.churn_probability,
            previous_promise_followups=0,
        )

        # Strategist Audit Log
        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Recovery Strategist",
                step_name="BROKEN_PROMISE_FOLLOWUP_STRATEGY",
                input_summary=f"Promise {promise.id} BROKEN. Profile: {intel_out.segment.value}, Precedents: n={strat_out.retrieved_precedent_count}",
                output_summary=f"Follow-up Action: {strat_out.action_type.value} (Empirical Conf: {strat_out.confidence:.4f})",
                decision=strat_out.action_type.value,
                confidence=strat_out.confidence,
                empirical_confidence=strat_out.confidence,
                llm_stated_confidence=strat_out.llm_stated_confidence,
                precedent_sample_size=strat_out.retrieved_precedent_count,
            )
        )

        # Policy Engine Audit Log
        self.recovery_repo.create_audit_log(
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:14]}",
                case_id=case.id,
                agent="Policy Engine",
                step_name="POLICY_GATE",
                input_summary=f"Follow-up Proposal: {strat_out.action_type.value}",
                output_summary=policy_res.reasoning,
                decision=policy_res.decision.value,
                confidence=1.0,
            )
        )

        # Action Executor Dispatch
        exec_res = ActionExecutor.execute(
            action_type=strat_out.action_type,
            policy_decision=policy_res.decision,
            amount=leak.amount,
            failure_reason=failure.failure_reason,
            attempt_number=failure.attempt_number + 1,
            incentive_percent=strat_out.incentive_percent,
            retry_delay_hours=strat_out.retry_delay_hours,
            channel=strat_out.channel,
            customer_contact=customer.email,
        )

        # Persist RecoveryAction Record
        action_rec = RecoveryAction(
            id=f"act_{uuid.uuid4().hex[:14]}",
            case_id=case.id,
            proposed_action=strat_out.action_type,
            policy_decision=policy_res.decision,
            policy_reasoning=policy_res.reasoning,
            incentive_percent=strat_out.incentive_percent,
            retry_delay_hours=strat_out.retry_delay_hours,
            outcome=exec_res.outcome,
            execution_details=f"[Promise Follow-Up #1] {exec_res.details}",
            executed_at=datetime.utcnow(),
        )
        self.recovery_repo.create_action(action_rec)

        if exec_res.communication_event_data:
            cdata = exec_res.communication_event_data
            self.recovery_repo.create_communication_event(
                CommunicationEvent(
                    id=f"comm_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    channel=cdata["channel"],
                    recipient=cdata["recipient"],
                    message_content=cdata["message_content"],
                    simulated_response=cdata["simulated_response"],
                    responded_at=datetime.utcnow(),
                )
            )

        if exec_res.recovered:
            case.status = CaseStatus.RECOVERED
            case.recovered_amount = exec_res.recovered_amount
            case.recovery_cost = (case.recovery_cost or 0.0) + exec_res.cost
            case.resolved_at = datetime.utcnow()
        elif policy_res.decision == PolicyDecision.ESCALATED:
            case.status = CaseStatus.ESCALATED
        elif policy_res.decision == PolicyDecision.REJECTED:
            case.status = CaseStatus.BLOCKED
        else:
            case.status = CaseStatus.FAILED

        # Recovery Analyst Write-Back
        try:
            RecoveryAnalystAgent.write_back_resolved_case(
                case_id=case.id,
                segment=customer.segment.value if customer.segment else "REGULAR",
                failure_reason=failure.failure_reason.value if failure else "UNKNOWN",
                action_taken=strat_out.action_type.value,
                channel=strat_out.channel,
                outcome=case.status.value,
                recovered_amount=case.recovered_amount,
            )
        except Exception as e:
            logger.error(f"Failed to write back follow-up outcome to ChromaDB: {e}")

        self.db.commit()
        return promise, case

    def list_promises(
        self,
        limit: int = 100,
        offset: int = 0,
        status: PromiseStatus | None = None,
    ) -> PromiseListResponse:
        promises = self.recovery_repo.get_all_promises(limit=limit, offset=offset, status=status)
        counts = self.recovery_repo.count_promises_by_status()

        summaries = []
        for p in promises:
            c = p.recovery_case
            cust = c.customer if c else None
            summaries.append(
                PromiseToPaySummary(
                    id=p.id,
                    case_id=p.case_id,
                    customer_id=cust.id if cust else None,
                    customer_name=cust.name if cust else "Unknown",
                    customer_email=cust.email if cust else "unknown@example.com",
                    customer_segment=cust.segment.value if cust and cust.segment else "REGULAR",
                    committed_amount=p.committed_amount,
                    committed_date=p.committed_date,
                    status=p.status,
                    follow_up_count=p.follow_up_count,
                    created_at=p.created_at,
                    resolved_at=p.resolved_at,
                )
            )

        return PromiseListResponse(
            items=summaries,
            total=counts["total"],
            pending_count=counts["pending"],
            kept_count=counts["kept"],
            broken_count=counts["broken"],
        )

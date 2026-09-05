import logging
import re
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.agents.graph import RecoveryAgentState, recovery_graph
from app.agents.recovery_analyst import RecoveryAnalystAgent
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService
from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.payment_failure import PaymentFailure
from app.models.promise_to_pay import PromiseStatus, PromiseToPay
from app.models.recovery_action import ActionType, PolicyDecision, RecoveryAction
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.models.transaction import TransactionStatus
from app.repositories.recovery import RecoveryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.promise import PromiseToPaySummary
from app.schemas.recovery import (
    CaseActionItem,
    CasesListResponse,
    CaseTimelineItem,
    RecoveryCaseDetail,
    RecoveryCaseSummary,
    RecoveryPrecedentItem,
)

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
        priority: str | None = None,
        reason: str | None = None,
        search: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> CasesListResponse:
        cases, total_count = self.recovery_repo.get_all_cases(
            limit=limit,
            offset=offset,
            status=status,
            priority=priority,
            reason=reason,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
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

            # Priority derivation (deterministic business formula based on transaction amount)
            amount = c.revenue_leak.amount if c.revenue_leak else 0.0
            if amount >= 20000.0:
                case_priority = "HIGH"
            elif amount < 5000.0:
                case_priority = "LOW"
            else:
                case_priority = "MEDIUM"

            # Recovery % computation
            if c.status == CaseStatus.RECOVERED and amount > 0:
                rec_rate = min(100.0, round((c.recovered_amount / amount) * 100.0, 1))
            elif c.status == CaseStatus.FAILED or c.status == CaseStatus.BLOCKED:
                rec_rate = 0.0
            else:
                score = c.revenue_leak.recoverability_score if c.revenue_leak else 0.5
                rec_rate = round(score * 100.0, 1)

            # Agents involved
            agent_names = list(dict.fromkeys([log.agent for log in c.audit_logs if log.agent]))
            if not agent_names:
                agent_names = ["Revenue Detective", "Customer Intelligence", "Recovery Strategist"]

            # Determine current human-readable step
            if c.status == CaseStatus.RECOVERED:
                step_str = "Resolution Complete"
            elif c.status == CaseStatus.ESCALATED:
                step_str = "Escalated to Human Queue"
            elif c.status == CaseStatus.BLOCKED:
                step_str = "Blocked by Policy Gate"
            elif c.status == CaseStatus.FAILED:
                step_str = "Execution Finished"
            elif c.status == CaseStatus.IN_PROGRESS:
                step_str = "Active Outreach"
            f_reason = (
                c.revenue_leak.payment_failure.failure_reason.value
                if (
                    c.revenue_leak
                    and c.revenue_leak.payment_failure
                    and c.revenue_leak.payment_failure.failure_reason
                )
                else None
            )
            f_code = (
                c.revenue_leak.payment_failure.raw_error_code
                if (c.revenue_leak and c.revenue_leak.payment_failure)
                else None
            )

            summaries.append(
                RecoveryCaseSummary(
                    id=c.id,
                    customer_id=c.customer_id,
                    customer_name=c.customer.name if c.customer else "Unknown",
                    customer_email=c.customer.email if c.customer else "unknown@example.com",
                    leak_type=(
                        c.revenue_leak.leak_type if c.revenue_leak else LeakType.TRANSACTION_FAILURE
                    ),
                    leak_amount=amount,
                    amount_at_risk=amount,
                    failure_reason=f_reason,
                    failure_code=f_code,
                    recoverability_score=(
                        c.revenue_leak.recoverability_score if c.revenue_leak else 0.5
                    ),
                    status=c.status,
                    priority=case_priority,
                    recovery_rate_percent=rec_rate,
                    recovered_amount=c.recovered_amount,
                    recovery_cost=c.recovery_cost,
                    has_sufficient_precedent=not has_insufficient_escalation,
                    precedent_count=precedent_count,
                    promise_status=promise_status,
                    agents_involved=agent_names,
                    current_step=step_str,
                    created_at=c.created_at,
                    resolved_at=c.resolved_at,
                )
            )

        return CasesListResponse(
            items=summaries,
            total=total_count,
            open_count=counts["open"],
            in_progress_count=counts["in_progress"],
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

        canonical_order = {
            "LEAK_DETECTION": 1,
            "PROFILE_ANALYSIS": 2,
            "STRATEGY_PROPOSAL": 3,
            "POLICY_GATE": 4,
            "DISPATCH_OUTCOME": 5,
            "PLAYBOOK_LEARNING_WRITEBACK": 6,
        }
        sorted_logs = sorted(
            case.audit_logs,
            key=lambda l: (
                canonical_order.get(l.step_name, 99),
                l.timestamp or datetime.min,
            ),
        )

        timeline = [
            CaseTimelineItem(
                id=log.id,
                agent=log.agent,
                step_name=log.step_name,
                input_summary=log.input_summary,
                output_summary=re.sub(
                    r"\((\d+)/(\d+)\s+attempts\)",
                    r"(\1 successful / \2 lifetime transactions)",
                    log.output_summary,
                ),
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
            for log in sorted_logs
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
                committed_amount=p.committed_amount,
                committed_date=p.committed_date,
                status=p.status,
                follow_up_count=p.follow_up_count,
                created_at=p.created_at,
                resolved_at=p.resolved_at,
            )
            for p in case.promises_to_pay
        ]

        # Determine priority and step for detail
        amount = case.revenue_leak.amount if case.revenue_leak else 0.0
        if amount >= 20000.0:
            case_priority = "HIGH"
        elif amount < 5000.0:
            case_priority = "LOW"
        else:
            case_priority = "MEDIUM"

        # Calculate Laplace smoothed payer reliability score
        past_txs = (
            case.customer.transactions if case.customer and case.customer.transactions else []
        )
        total_tx = len(past_txs)
        success_tx = sum(1 for t in past_txs if t.status == TransactionStatus.SUCCESS)
        reliability = round((success_tx + 2) / (total_tx + 4), 4)

        if case.status == CaseStatus.RECOVERED and amount > 0:
            rec_rate = min(100.0, round((case.recovered_amount / amount) * 100.0, 1))
        elif case.status in [CaseStatus.FAILED, CaseStatus.BLOCKED]:
            rec_rate = 0.0
        else:
            score = case.revenue_leak.recoverability_score if case.revenue_leak else 0.5
            rec_rate = round(score * 100.0, 1)

        agent_names = list(dict.fromkeys([log.agent for log in case.audit_logs if log.agent]))
        if not agent_names:
            agent_names = ["Revenue Detective", "Customer Intelligence", "Recovery Strategist"]

        if case.status == CaseStatus.RECOVERED:
            step_str = "Resolution Complete"
        elif case.status == CaseStatus.ESCALATED:
            step_str = "Escalated to Human Queue"
        elif case.status == CaseStatus.BLOCKED:
            step_str = "Blocked by Policy Gate"
        elif case.status == CaseStatus.FAILED:
            step_str = "Execution Finished"
        elif case.status == CaseStatus.IN_PROGRESS:
            step_str = "Active Outreach"
        else:
            step_str = "Pending Evaluation"

        f_reason = (
            case.revenue_leak.payment_failure.failure_reason.value
            if (
                case.revenue_leak
                and case.revenue_leak.payment_failure
                and case.revenue_leak.payment_failure.failure_reason
            )
            else None
        )
        f_code = (
            case.revenue_leak.payment_failure.raw_error_code
            if (case.revenue_leak and case.revenue_leak.payment_failure)
            else None
        )

        # Real-time ChromaDB Grounded Precedent Retrieval (Dense Vector Search)
        retrieved_precedents: list[RecoveryPrecedentItem] = []
        if f_reason:
            try:
                chroma_cases = RecoveryPlaybookService.query_similar_cases(
                    failure_reason=f_reason,
                    leak_type=(
                        case.revenue_leak.leak_type.value
                        if case.revenue_leak and case.revenue_leak.leak_type
                        else None
                    ),
                    k=5,
                )
                for c_meta in chroma_cases:
                    retrieved_precedents.append(
                        RecoveryPrecedentItem(
                            case_id=str(c_meta.get("case_id", "")),
                            failure_reason=str(c_meta.get("failure_reason", f_reason)),
                            action_taken=str(c_meta.get("action_taken", "RETRY")),
                            channel=str(c_meta.get("channel", "NONE")),
                            outcome=str(c_meta.get("outcome", "UNKNOWN")),
                            recovered_amount=float(c_meta.get("recovered_amount", 0.0)),
                            is_recovered=bool(c_meta.get("is_recovered", False)),
                            segment=c_meta.get("segment"),
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to query ChromaDB precedents for case {case.id}: {e}")

        return RecoveryCaseDetail(
            id=case.id,
            customer_id=case.customer_id,
            customer_name=case.customer.name if case.customer else "Unknown",
            customer_email=case.customer.email if case.customer else "unknown@example.com",
            leak_type=(
                case.revenue_leak.leak_type if case.revenue_leak else LeakType.TRANSACTION_FAILURE
            ),
            leak_amount=amount,
            amount_at_risk=amount,
            failure_reason=f_reason,
            failure_code=f_code,
            payer_reliability_score=reliability,
            recoverability_score=(
                case.revenue_leak.recoverability_score if case.revenue_leak else 0.5
            ),
            status=case.status,
            priority=case_priority,
            recovery_rate_percent=rec_rate,
            recovered_amount=case.recovered_amount,
            recovery_cost=case.recovery_cost,
            has_sufficient_precedent=not has_insufficient_escalation,
            precedent_count=precedent_count,
            promise_status=promise_status,
            agents_involved=agent_names,
            current_step=step_str,
            created_at=case.created_at,
            resolved_at=case.resolved_at,
            actions=actions,
            timeline=timeline,
            promises=promises,
            retrieved_precedents=retrieved_precedents,
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
            "reproposal_count": 0,
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

        # 2. Persist or Update Revenue Leak
        leak = failure.revenue_leaks[0] if failure.revenue_leaks else None
        if not leak:
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
        else:
            leak.leak_type = det_out.leak_type if det_out else leak.leak_type
            leak.amount = det_out.amount if det_out else leak.amount
            leak.confidence = det_out.confidence if det_out else leak.confidence
            leak.recoverability_score = (
                det_out.recoverability_score if det_out else leak.recoverability_score
            )
            self.db.commit()

        # 3. Persist or Update Recovery Case
        case = leak.recovery_case
        if not case:
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
            channels_str = (
                ", ".join(intel_out.available_channels) if intel_out.available_channels else "EMAIL"
            )
            alternate_rails_str = (
                ", ".join(intel_out.alternate_rails) if intel_out.has_alternate_rail else "None"
            )
            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Customer Intelligence",
                    step_name="PROFILE_ANALYSIS",
                    input_summary=f"Customer: {customer.name}, Channels: {channels_str}",
                    output_summary=(
                        f"Reliability: {intel_out.payer_reliability_score:.1%} ({intel_out.successful_past_transactions} successful / {intel_out.total_past_transactions} lifetime transactions), "
                        f"Timing: {intel_out.timing_band}, Alternate Rails: {alternate_rails_str}, "
                        f"Empirical Conf: {intel_out.confidence:.4f} (n={intel_out.precedent_sample_size})"
                    ),
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
                    input_summary=(
                        f"Leak: ₹{tx.amount:,.2f}, "
                        f"Reliability: {intel_out.payer_reliability_score:.1%} if intel_out else 'N/A', "
                        f"Precedents: n={strat_out.retrieved_precedent_count} (Insufficient: {strat_out.insufficient_precedent})"
                    ),
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
                failure_reason=failure.failure_reason.value,
                action_taken=strat_out.action_type.value if strat_out else "RETRY",
                channel=strat_out.channel if strat_out else None,
                outcome=case.status.value,
                recovered_amount=recovered_amount if recovered else 0.0,
            )
            # Recovery Analyst Audit Log
            self.recovery_repo.create_audit_log(
                AuditLog(
                    id=f"log_{uuid.uuid4().hex[:14]}",
                    case_id=case.id,
                    agent="Recovery Analyst",
                    step_name="PLAYBOOK_LEARNING_WRITEBACK",
                    input_summary=f"Case: {case.id}, Reason: {failure.failure_reason.value}, Outcome: {case.status.value}",
                    output_summary=f"Stored case in ChromaDB recovery_playbook for grounded RAG precedent retrieval (Recovered: ₹{recovered_amount:,.2f})",
                    decision="PLAYBOOK_UPDATED",
                    confidence=1.0,
                )
            )
        except Exception as e:
            logger.error(f"Failed to write back case {case.id} to recovery playbook: {e}")

        self.db.commit()
        return case


# Compatibility alias
RecoveryService = RecoveryOrchestratorService

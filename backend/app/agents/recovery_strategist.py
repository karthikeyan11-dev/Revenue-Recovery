import logging

from app.integrations.llm.client import LLMClient
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService
from app.models.payment_failure import FailureReason
from app.models.recovery_action import ActionType
from app.repositories.recovery import RecoveryRepository
from app.schemas.customer import CustomerIntelligenceOutput
from app.schemas.detective import RevenueDetectiveOutput
from app.schemas.strategist import ProposedRecoveryAction

logger = logging.getLogger("app.agents.strategist")


class RecoveryStrategistAgent:
    """
    Recovery Strategist Agent Node.
    Synthesizes diagnostic leak classification with 4 payment-native customer signals
    and RAG Playbook historical precedents to propose a deterministic, bounded recovery action.
    """

    @classmethod
    def propose_action(
        cls,
        detective_output: RevenueDetectiveOutput,
        intel_output: CustomerIntelligenceOutput,
        failure_reason: str | FailureReason,
        is_reproposal: bool = False,
    ) -> ProposedRecoveryAction:
        f_reason = (
            failure_reason.value if isinstance(failure_reason, FailureReason) else failure_reason
        )

        # 1. RAG Playbook Precedent Retrieval (Dense Chroma Vector Search)
        retrieved_cases = RecoveryPlaybookService.query_similar_cases(
            failure_reason=f_reason,
            k=5,
        )
        k = len(retrieved_cases)

        # 2. Empirical Precedent Recovery Rate Calculation (Laplace Smoothed)
        successes = sum(1 for r in retrieved_cases if r.get("outcome") in ("RECOVERED", "SUCCESS"))
        empirical_confidence = RecoveryRepository.calculate_laplace_confidence(
            successes=successes,
            total=k,
            prior_successes=2,
            prior_total=4,
        )

        # 3. Insufficient Precedent Evaluation (Threshold: min 5 cases)
        insufficient_precedent = k < 5

        logger.info(
            f"[RecoveryStrategist] RAG Playbook Retrieval: {k} cases retrieved (successes={successes}), "
            f"empirical_confidence={empirical_confidence:.4f}, insufficient_precedent={insufficient_precedent}, is_reproposal={is_reproposal}"
        )

        # 4. Determine Primary Available Outreach Channel
        available = intel_output.available_channels or ["EMAIL"]
        primary_channel = (
            "WHATSAPP" if "WHATSAPP" in available else ("EMAIL" if "EMAIL" in available else "SMS")
        )

        # 5. Deterministic Bounded Strategy Selection Matrix
        reason_upper = str(f_reason).upper()
        if is_reproposal:
            # Policy-compliant fallback upon rejection: switch to safe direct payment link or compliant outreach
            action_type = ActionType.SEND_PAYMENT_LINK
            retry_delay_hours = 0
            incentive_percent = 0.0
            channel = primary_channel
            message_tone = "INFORMATIVE"
            base_reasoning = (
                f"[Re-proposal] Prior proposal rejected by policy. Falling back to compliant "
                f"direct payment link via {channel}."
            )
        elif "NETWORK" in reason_upper or "GATEWAY" in reason_upper:
            # Transient technical failure: smart API retry with jitter
            action_type = ActionType.RETRY
            retry_delay_hours = 1
            incentive_percent = 0.0
            channel = None
            message_tone = "NEUTRAL"
            base_reasoning = "Transient network/gateway error detected. Smart automated retry scheduled with 1h backoff."
        elif "INSUFFICIENT_FUNDS" in reason_upper:
            # If customer has alternate successful rail (e.g. UPI), dispatch payment link for rail switch
            if intel_output.has_alternate_rail:
                action_type = ActionType.SEND_PAYMENT_LINK
                retry_delay_hours = 0
                incentive_percent = 0.0
                channel = primary_channel
                message_tone = "INFORMATIVE"
                base_reasoning = (
                    f"Insufficient funds on primary rail. Customer has past successful alternate rail "
                    f"({', '.join(intel_output.alternate_rails)}). Dispatched alternate rail payment link via {channel}."
                )
            else:
                # Liquidity replenishment window: 12h delayed retry for bank/salary recharge
                action_type = ActionType.RETRY
                retry_delay_hours = 12
                incentive_percent = 0.0
                channel = None
                message_tone = "NEUTRAL"
                base_reasoning = "Insufficient funds failure detected. Smart retry scheduled for optimal 12-hour banking recharge window."
        elif "USER_DROPOFF" in reason_upper or "AUTHENTICATION" in reason_upper:
            # Checkout friction/drop-off: interactive WhatsApp 1-click recovery with modest completion coupon
            action_type = (
                ActionType.SEND_WHATSAPP
                if "WHATSAPP" in available
                else ActionType.SEND_PAYMENT_LINK
            )
            retry_delay_hours = 0
            incentive_percent = 5.0
            channel = "WHATSAPP" if "WHATSAPP" in available else primary_channel
            message_tone = "EMPATHETIC"
            base_reasoning = (
                f"Checkout drop-off/friction detected ({f_reason}). Dispatched interactive recovery "
                f"via {channel} with {incentive_percent:.0f}% completion incentive."
            )
        elif "LIMIT_EXCEEDED" in reason_upper:
            # Card limit reached: dispatch 1-Click WhatsApp link with dynamic 3% discount to encourage alternate rail (UPI)
            action_type = (
                ActionType.SEND_WHATSAPP
                if "WHATSAPP" in available
                else ActionType.SEND_PAYMENT_LINK
            )
            retry_delay_hours = 0
            incentive_percent = 3.0
            channel = "WHATSAPP" if "WHATSAPP" in available else primary_channel
            message_tone = "EMPATHETIC"
            base_reasoning = (
                f"Card limit reached ({f_reason}). Dispatched alternate rail 1-click link via {channel} "
                f"with {incentive_percent:.0f}% split-payment completion incentive to convert transaction."
            )
        elif "EXPIRED_CARD" in reason_upper:
            action_type = ActionType.SEND_PAYMENT_LINK
            retry_delay_hours = 0
            incentive_percent = 0.0
            channel = primary_channel
            message_tone = "URGENT"
            if intel_output.has_alternate_rail:
                base_reasoning = (
                    f"Card expired ({f_reason}). Customer has verified alternate rails "
                    f"({', '.join(intel_output.alternate_rails)}). Dispatched alternate rail payment link via {channel}."
                )
            else:
                base_reasoning = (
                    f"Payment card expired ({f_reason}). Dispatched secure alternative payment method link "
                    f"via {channel}."
                )
        elif (
            detective_output.recoverability_score >= 0.80
            and intel_output.payer_reliability_score >= 0.70
        ):
            action_type = ActionType.RETRY
            retry_delay_hours = 4
            incentive_percent = 0.0
            channel = None
            message_tone = "NEUTRAL"
            base_reasoning = (
                f"High recoverability ({detective_output.recoverability_score:.2f}) with high reliability repeat payer "
                f"({intel_output.payer_reliability_score:.1%}). Smart API retry scheduled."
            )
        else:
            action_type = ActionType.SEND_PAYMENT_LINK
            retry_delay_hours = 0
            incentive_percent = 0.0
            channel = primary_channel
            message_tone = "INFORMATIVE"
            base_reasoning = (
                f"Standard recovery link dispatched across available channel ({primary_channel})."
            )

        # 6. Format Grounding Evidence for LLM Tactical Justification
        if retrieved_cases:
            grounding_text = "\n".join(
                [
                    f"  - Precedent #{i+1}: Action={r.get('action_taken')}, Channel={r.get('channel')}, "
                    f"Outcome={r.get('outcome')}, Recovered=₹{float(r.get('recovered_amount', 0.0)):,.2f}"
                    for i, r in enumerate(retrieved_cases)
                ]
            )
        else:
            grounding_text = "  - No past precedent cases in playbook (cold start / thin evidence)."

        system_prompt = (
            "You are the Recovery Strategist AI agent in an autonomous revenue recovery system. "
            "Synthesize the leak diagnostics, payment-native customer signals, and retrieved historical precedents from the recovery playbook "
            "to provide compelling tactical justification (1-2 sentences) for the recovery intervention. "
            "Reference the precedent outcomes where relevant."
        )
        user_prompt = (
            f"Leak Amount: ₹{detective_output.amount:,.2f}\n"
            f"Leak Recoverability: {detective_output.recoverability_score:.2f}\n"
            f"Payer Reliability Score: {intel_output.payer_reliability_score:.1%} ({intel_output.successful_past_transactions}/{intel_output.total_past_transactions} past attempts)\n"
            f"Failure Timing Context: {intel_output.timing_band} ({intel_output.hours_since_failure:.1f}h elapsed, {intel_output.recent_failure_count} recent attempts)\n"
            f"Alternate Successful Rails: {', '.join(intel_output.alternate_rails) if intel_output.has_alternate_rail else 'None on record'}\n"
            f"Available Channels: {', '.join(intel_output.available_channels)}\n"
            f"Selected Action: {action_type.value}\n"
            f"Channel: {channel or 'Direct API Retry'}\n"
            f"Incentive Discount: {incentive_percent}%\n"
            f"Retrieved Precedent Cases from Recovery Playbook ({k} cases found):\n"
            f"{grounding_text}\n"
            "Provide strategic tactical justification grounded in the retrieved precedents."
        )

        llm_reasoning = LLMClient.generate_reasoning(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_text=base_reasoning,
        )

        llm_stated_confidence = 0.88 if retrieved_cases else 0.70

        return ProposedRecoveryAction(
            action_type=action_type,
            retry_delay_hours=retry_delay_hours,
            incentive_percent=incentive_percent,
            channel=channel,
            message_tone=message_tone,
            confidence=empirical_confidence,
            insufficient_precedent=insufficient_precedent,
            retrieved_precedent_count=k,
            retrieved_precedents=retrieved_cases,
            reasoning=llm_reasoning,
            llm_stated_confidence=llm_stated_confidence,
        )

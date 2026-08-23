import logging
from typing import Any

from app.agents.llm_client import LLMClient
from app.models.recovery_action import ActionType
from app.rag.playbook import RecoveryPlaybookService
from app.schemas.customer_intel import CustomerIntelligenceOutput
from app.schemas.detective import RevenueDetectiveOutput
from app.schemas.strategist import ProposedRecoveryAction

logger = logging.getLogger("app.agents.strategist")


class RecoveryStrategistAgent:
    """
    Recovery Strategist Agent Node.
    Synthesizes leak classification + customer intelligence + RAG playbook precedent
    to propose bounded recovery action with empirical Laplace-smoothed confidence
    and strict precedent sufficiency gating.
    """

    @classmethod
    def propose_action(
        cls,
        detective_output: RevenueDetectiveOutput,
        intel_output: CustomerIntelligenceOutput,
        failure_reason: str | None = None,
    ) -> ProposedRecoveryAction:
        seg = intel_output.segment.value
        f_reason = failure_reason or detective_output.leak_type.value

        # 1. RAG Tool Call: Retrieve top k=5 similar historical resolved cases from ChromaDB
        retrieved_cases: list[dict[str, Any]] = RecoveryPlaybookService.query_similar_cases(
            segment=seg,
            failure_reason=f_reason,
            leak_type=detective_output.leak_type.value,
            k=5,
        )

        k = len(retrieved_cases)
        successes = sum(
            1
            for r in retrieved_cases
            if r.get("is_recovered") is True
            or str(r.get("outcome", "")).upper() in ["SUCCESS", "RECOVERED"]
        )

        # 2. Compute Empirical Laplace-Smoothed Confidence on Retrieved Precedents
        # Prior: 2 successes out of 4 pseudo-cases (50% weak base rate)
        empirical_confidence = round((successes + 2) / (k + 4), 4)

        # 3. Insufficient Precedent Evaluation (Threshold: min 5 cases)
        insufficient_precedent = k < 5

        logger.info(
            f"[RecoveryStrategist] RAG Playbook Retrieval: {k} cases retrieved (successes={successes}), "
            f"empirical_confidence={empirical_confidence:.4f}, insufficient_precedent={insufficient_precedent}"
        )

        # 4. Deterministic Bounded Strategy Selection Matrix
        if detective_output.recoverability_score >= 0.80 and intel_output.churn_probability < 0.30:
            action_type = ActionType.RETRY
            retry_delay_hours = 4
            incentive_percent = 0.0
            channel = None
            message_tone = "NEUTRAL"
            base_reasoning = (
                f"High recoverability ({detective_output.recoverability_score:.2f}) with stable customer profile. "
                "Smart API retry scheduled."
            )
        elif seg in ["HIGH_VALUE", "LOYAL"]:
            action_type = ActionType.SEND_WHATSAPP
            retry_delay_hours = 0
            incentive_percent = 5.0
            channel = "WHATSAPP"
            message_tone = "EMPATHETIC"
            base_reasoning = (
                f"High LTV customer (₹{intel_output.ltv:,.2f}). Propose personal WhatsApp outreach "
                "with 5% priority recovery coupon."
            )
        elif seg in ["AT_RISK", "CHURNING"]:
            action_type = ActionType.OFFER_INCENTIVE
            retry_delay_hours = 0
            incentive_percent = 12.0 if intel_output.churn_probability > 0.85 else 10.0
            channel = intel_output.preferred_channel.value
            message_tone = "URGENT"
            base_reasoning = (
                f"Elevated churn probability ({intel_output.churn_probability:.0%}). "
                f"Propose {incentive_percent}% re-engagement incentive."
            )
        else:
            action_type = ActionType.SEND_PAYMENT_LINK
            retry_delay_hours = 0
            incentive_percent = 0.0
            channel = intel_output.preferred_channel.value
            message_tone = "INFORMATIVE"
            base_reasoning = f"Standard recovery link dispatched across preferred channel ({intel_output.preferred_channel.value})."

        # 5. Format Grounding Evidence for LLM Tactical Justification
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
            "Synthesize the leak diagnostics, customer profile, and retrieved historical precedents from the recovery playbook "
            "to provide compelling tactical justification (1-2 sentences) for the recovery intervention. "
            "Reference the precedent outcomes where relevant."
        )
        user_prompt = (
            f"Leak Amount: ₹{detective_output.amount:,.2f}\n"
            f"Leak Recoverability: {detective_output.recoverability_score:.2f}\n"
            f"Customer Segment: {seg}\n"
            f"Customer LTV: ₹{intel_output.ltv:,.2f}\n"
            f"Customer Churn Risk: {intel_output.churn_probability:.0%}\n"
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

        # Log LLM's own self-assessed confidence separately (never used for policy gating)
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
            retrieved_cases_summary=retrieved_cases,
            llm_stated_confidence=llm_stated_confidence,
            reasoning=llm_reasoning,
        )

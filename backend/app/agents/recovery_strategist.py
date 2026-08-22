import logging

from app.models.recovery_action import ActionType
from app.schemas.customer_intel import CustomerIntelligenceOutput
from app.schemas.detective import RevenueDetectiveOutput
from app.schemas.strategist import ProposedRecoveryAction

logger = logging.getLogger("app.agents.strategist")


class RecoveryStrategistAgent:
    """
    Recovery Strategist Agent Node.
    Synthesizes leak classification + customer intelligence to propose bounded recovery action.
    """

    @classmethod
    def propose_action(
        cls,
        detective_output: RevenueDetectiveOutput,
        intel_output: CustomerIntelligenceOutput,
    ) -> ProposedRecoveryAction:
        seg = intel_output.segment.value

        # Strategy Decision Tree
        if detective_output.recoverability_score >= 0.80 and intel_output.churn_probability < 0.30:
            return ProposedRecoveryAction(
                action_type=ActionType.RETRY,
                retry_delay_hours=4,
                reasoning=f"High recoverability ({detective_output.recoverability_score:.2f}) with stable customer profile. Fast smart retry scheduled.",
            )

        if seg in ["HIGH_VALUE", "LOYAL"]:
            return ProposedRecoveryAction(
                action_type=ActionType.SEND_WHATSAPP,
                channel="WHATSAPP",
                incentive_percent=5.0,
                message_tone="EMPATHETIC",
                reasoning=f"High LTV customer (₹{intel_output.ltv:,.2f}). Propose personal WhatsApp outreach with 5% priority recovery coupon.",
            )

        if seg in ["AT_RISK", "CHURNING"]:
            return ProposedRecoveryAction(
                action_type=ActionType.OFFER_INCENTIVE,
                channel=intel_output.preferred_channel.value,
                incentive_percent=10.0,
                message_tone="URGENT",
                reasoning=f"Elevated churn probability ({intel_output.churn_probability:.0%}). Propose 10% re-engagement incentive.",
            )

        return ProposedRecoveryAction(
            action_type=ActionType.SEND_PAYMENT_LINK,
            channel=intel_output.preferred_channel.value,
            message_tone="INFORMATIVE",
            reasoning=f"Standard recovery link dispatched across preferred channel ({intel_output.preferred_channel.value}).",
        )

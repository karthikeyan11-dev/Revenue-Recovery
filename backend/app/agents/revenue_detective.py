import logging

from app.models.payment_failure import PaymentFailure
from app.models.revenue_leak import LeakType
from app.schemas.detective import RevenueDetectiveOutput

logger = logging.getLogger("app.agents.detective")


class RevenueDetectiveAgent:
    """
    Revenue Detective Agent Node.
    Analyzes payment failure telemetry and classifies leak category with recoverability score.
    """

    @classmethod
    def analyze(cls, failure: PaymentFailure) -> RevenueDetectiveOutput:
        reason = failure.failure_reason.value
        amount = failure.transaction.amount

        # Soft failures have high recoverability
        if reason in ["INSUFFICIENT_FUNDS", "NETWORK_ERROR", "USER_DROPOFF"]:
            leak_type = LeakType.TRANSACTION_FAILURE
            recoverability = 0.85
            reasoning = f"Transient/soft decline ({reason}). High potential for smart retry or checkout link recovery."
        elif reason == "EXPIRED_CARD":
            leak_type = (
                LeakType.SUBSCRIPTION_LAPSE
                if failure.attempt_number > 1
                else LeakType.TRANSACTION_FAILURE
            )
            recoverability = 0.40
            reasoning = "Card expired. Requires interactive customer outreach to update payment credentials."
        else:
            leak_type = LeakType.TRANSACTION_FAILURE
            recoverability = 0.55
            reasoning = f"Bank decline code ({reason}). Moderate recoverability via alternate payment rails."

        return RevenueDetectiveOutput(
            failure_id=failure.id,
            leak_type=leak_type,
            amount=amount,
            confidence=0.92,
            recoverability_score=recoverability,
            reasoning=reasoning,
        )

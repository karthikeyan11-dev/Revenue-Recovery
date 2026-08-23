import random

from app.models.payment_failure import FailureReason


class PaymentSimulator:
    """
    Simulates payment retry outcomes based on failure reason and delay.
    """

    # Base recovery probabilities by failure category when retried smartly
    BASE_PROBABILITIES = {
        FailureReason.NETWORK_ERROR: 0.85,
        FailureReason.INSUFFICIENT_FUNDS: 0.65,
        FailureReason.BANK_DECLINED: 0.50,
        FailureReason.AUTHENTICATION_FAILED: 0.45,
        FailureReason.LIMIT_EXCEEDED: 0.40,
        FailureReason.EXPIRED_CARD: 0.05,  # Needs new card/link, hard failure
        FailureReason.USER_DROPOFF: 0.70,
    }

    @classmethod
    def simulate_retry(
        cls,
        failure_reason: FailureReason,
        attempt_number: int,
        delay_hours: int = 0,
    ) -> tuple[bool, str]:
        base_prob = cls.BASE_PROBABILITIES.get(failure_reason, 0.40)

        # Decay probability with each subsequent attempt
        decay = max(0.1, 1.0 - (attempt_number * 0.18))
        effective_prob = base_prob * decay

        # Boost slightly if delayed appropriately for banking recharge
        if delay_hours >= 12 and failure_reason == FailureReason.INSUFFICIENT_FUNDS:
            effective_prob = min(0.90, effective_prob + 0.15)

        success = random.random() < effective_prob

        if success:
            return True, f"Smart retry attempt #{attempt_number} succeeded (Bank Auth OK)"
        return False, f"Smart retry attempt #{attempt_number} declined by issuer"

import random

from app.models.payment_failure import FailureReason


class PaymentSimulator:
    """
    Simulates payment retry outcomes based on failure reason and delay.
    """

    # Realistic base recovery probabilities for blind payment gateway retries
    BASE_PROBABILITIES = {
        FailureReason.NETWORK_ERROR: 0.85,  # Transient gateway timeout / connection drop
        FailureReason.INSUFFICIENT_FUNDS: 0.25,  # Needs delayed window or alternate rail
        FailureReason.BANK_DECLINED: 0.10,  # Issuer decline: blind retry rarely works, needs alternate rail
        FailureReason.AUTHENTICATION_FAILED: 0.05,  # 3DS / OTP failed: blind retry cannot authenticate
        FailureReason.LIMIT_EXCEEDED: 0.10,  # Card limit exceeded: requires user limit adjustment or rail switch
        FailureReason.EXPIRED_CARD: 0.02,  # Hard card expiration: requires new payment method
        FailureReason.USER_DROPOFF: 0.05,  # Checkout abandoned: blind retry cannot complete without user
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

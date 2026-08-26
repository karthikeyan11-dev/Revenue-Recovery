from app.models.payment_failure import FailureReason


def normalize_razorpay_failure_reason(
    error_code: str | None = None,
    error_reason: str | None = None,
    error_description: str | None = None,
) -> FailureReason:
    """
    Maps authentic Razorpay error codes, reasons, and descriptions to internal FailureReason enum.
    """
    tokens = " ".join(filter(None, [error_code, error_reason, error_description])).lower()

    if any(
        t in tokens for t in ["insufficient", "low_balance", "funds", "balance_insufficient"]
    ):
        return FailureReason.INSUFFICIENT_FUNDS
    elif any(
        t in tokens
        for t in [
            "cancelled",
            "dropoff",
            "abandoned",
            "user_cancelled",
            "back_button",
            "payment_cancelled",
        ]
    ):
        return FailureReason.USER_DROPOFF
    elif any(
        t in tokens for t in ["auth", "otp", "3ds", "authentication_failed", "wrong_otp", "pin"]
    ):
        return FailureReason.AUTHENTICATION_FAILED
    elif any(t in tokens for t in ["expired", "card_expired", "expiry", "card_expiry"]):
        return FailureReason.EXPIRED_CARD
    elif any(t in tokens for t in ["limit", "amount_exceeded", "daily_limit", "max_amount"]):
        return FailureReason.LIMIT_EXCEEDED
    elif any(
        t in tokens
        for t in ["network", "timeout", "gateway_error", "server_error", "bad_gateway"]
    ):
        return FailureReason.NETWORK_ERROR
    else:
        return FailureReason.BANK_DECLINED

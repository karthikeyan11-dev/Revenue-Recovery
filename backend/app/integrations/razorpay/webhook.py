import hashlib
import hmac
import logging

from app.config import settings

logger = logging.getLogger("app.integrations.razorpay.webhook")


def verify_razorpay_webhook_signature(
    body_bytes: bytes,
    signature: str,
    secret: str | None = None,
) -> bool:
    """
    Verifies Razorpay X-Razorpay-Signature HMAC-SHA256 digest against raw request body bytes.
    """
    sec = secret or settings.RAZORPAY_WEBHOOK_SECRET
    if not sec:
        logger.warning(
            "[RazorpayClient:Webhook] RAZORPAY_WEBHOOK_SECRET is empty. Webhook signature verification skipped in dev mode."
        )
        return True

    if not signature:
        logger.warning("[RazorpayClient:Webhook] Missing X-Razorpay-Signature header.")
        return False

    try:
        expected_signature = hmac.new(
            sec.encode("utf-8"),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        is_valid = hmac.compare_digest(expected_signature, signature)
        if not is_valid:
            logger.warning(
                f"[RazorpayClient:Webhook] Signature mismatch. Expected: {expected_signature}, Got: {signature}"
            )
        return is_valid
    except Exception as e:
        logger.error(f"[RazorpayClient:Webhook] Signature verification error: {e}")
        return False

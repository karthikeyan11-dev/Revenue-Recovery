import logging
import uuid
from datetime import datetime

import httpx

from app.config import settings
from app.integrations.razorpay.normalizer import normalize_razorpay_failure_reason
from app.integrations.razorpay.webhook import verify_razorpay_webhook_signature
from app.models.payment_failure import FailureReason

logger = logging.getLogger("app.integrations.razorpay.client")


class RazorpayClient:
    """
    Razorpay REST API Client for Orders API and Webhook Verification.
    Operates in live test mode when credentials exist, and degrades gracefully
    to high-fidelity mock IDs when credentials are intentionally omitted.
    """

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(
        self,
        key_id: str | None = None,
        key_secret: str | None = None,
        webhook_secret: str | None = None,
    ):
        self.key_id = (settings.RAZORPAY_KEY_ID if key_id is None else key_id).strip()
        self.key_secret = (
            settings.RAZORPAY_KEY_SECRET if key_secret is None else key_secret
        ).strip()
        self.webhook_secret = (
            settings.RAZORPAY_WEBHOOK_SECRET if webhook_secret is None else webhook_secret
        ).strip()

    @property
    def is_configured(self) -> bool:
        return bool(
            self.key_id
            and self.key_secret
            and not self.key_id.startswith("your_")
            and not self.key_secret.startswith("your_")
        )

    def create_order(
        self,
        amount_rupees: float,
        currency: str = "INR",
        receipt: str | None = None,
        notes: dict | None = None,
    ) -> dict:
        """
        Creates a genuine Razorpay Order via POST /v1/orders in test mode.
        If credentials are not configured (offline mode), generates a mock order ID.
        If credentials are provided but invalid (401/403), raises ValueError to surface config errors.
        """
        if not self.is_configured:
            mock_order_id = f"order_mock_{uuid.uuid4().hex[:14]}"
            logger.info(
                f"[RazorpayClient:Offline] Credentials not configured. Generated mock order {mock_order_id} (₹{amount_rupees:,.2f})"
            )
            return {
                "id": mock_order_id,
                "entity": "order",
                "amount": int(round(amount_rupees * 100)),
                "amount_paid": 0,
                "amount_due": int(round(amount_rupees * 100)),
                "currency": currency,
                "receipt": receipt,
                "status": "created",
                "attempts": 0,
                "notes": notes or {},
                "created_at": int(datetime.utcnow().timestamp()),
                "is_mock": True,
            }

        amount_paise = int(round(amount_rupees * 100))
        payload = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt or f"rcpt_{uuid.uuid4().hex[:10]}",
            "notes": notes or {"source": "ai_revenue_recovery_orchestrator"},
        }

        try:
            with httpx.Client(auth=(self.key_id, self.key_secret), timeout=10.0) as client:
                response = client.post(f"{self.BASE_URL}/orders", json=payload)

            if response.status_code in (200, 201):
                data = response.json()
                logger.info(
                    f"[RazorpayClient:Live] Successfully created real Razorpay order {data.get('id')} for ₹{amount_rupees:,.2f}"
                )
                data["is_mock"] = False
                return data

            if response.status_code in (401, 403):
                err_msg = (
                    f"Razorpay API authentication failed ({response.status_code}): {response.text}"
                )
                logger.error(f"[RazorpayClient:Error] {err_msg}")
                raise ValueError(err_msg)

            logger.warning(
                f"[RazorpayClient:Warning] Order creation failed with HTTP {response.status_code}: {response.text}. Using fallback order."
            )
            return {
                "id": f"order_fallback_{uuid.uuid4().hex[:14]}",
                "entity": "order",
                "amount": amount_paise,
                "currency": currency,
                "receipt": receipt,
                "status": "created",
                "is_mock": True,
            }

        except httpx.RequestError as e:
            logger.error(
                f"[RazorpayClient:NetworkError] Network failure reaching Razorpay API: {e}"
            )
            return {
                "id": f"order_offline_{uuid.uuid4().hex[:14]}",
                "entity": "order",
                "amount": amount_paise,
                "currency": currency,
                "receipt": receipt,
                "status": "created",
                "is_mock": True,
            }

    def fetch_order(self, order_id: str) -> dict | None:
        """Fetches order metadata from Razorpay Orders API."""
        if not self.is_configured or order_id.startswith("order_mock_"):
            return None

        try:
            with httpx.Client(auth=(self.key_id, self.key_secret), timeout=10.0) as client:
                resp = client.get(f"{self.BASE_URL}/orders/{order_id}")
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            logger.error(f"[RazorpayClient:FetchError] Failed to fetch order {order_id}: {e}")
            return None

    def verify_webhook_signature(
        self,
        body_bytes: bytes,
        signature: str,
        secret: str | None = None,
    ) -> bool:
        """Verifies HMAC signature for incoming webhooks."""
        return verify_razorpay_webhook_signature(
            body_bytes=body_bytes,
            signature=signature,
            secret=secret or self.webhook_secret,
        )

    @staticmethod
    def normalize_failure_reason(
        error_code: str | None = None,
        error_reason: str | None = None,
        error_description: str | None = None,
    ) -> FailureReason:
        """Maps authentic Razorpay error codes to FailureReason."""
        return normalize_razorpay_failure_reason(
            error_code=error_code,
            error_reason=error_reason,
            error_description=error_description,
        )

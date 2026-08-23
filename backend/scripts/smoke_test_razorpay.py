"""
Razorpay Test API Smoke Test Script.
Verifies:
1. Real test-mode Order creation (POST /v1/orders) using RAZORPAY_KEY_ID & RAZORPAY_KEY_SECRET from .env.
2. Graceful offline/mock mode when credentials are not configured.
3. Cryptographic HMAC-SHA256 signature verification for webhook payloads.
"""

import json
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.integrations.razorpay_client import RazorpayClient


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main():
    print_banner("RAZORPAY INTEGRATION SMOKE TEST")

    print(
        f"Key ID Configured: {'Yes (' + settings.RAZORPAY_KEY_ID[:8] + '...)' if settings.RAZORPAY_KEY_ID else 'No'}"
    )
    print(f"Key Secret Configured: {'Yes (***)' if settings.RAZORPAY_KEY_SECRET else 'No'}")
    print(f"Webhook Secret Configured: {'Yes (***)' if settings.RAZORPAY_WEBHOOK_SECRET else 'No'}")

    client = RazorpayClient()
    print(
        f"Razorpay Client Mode: {'LIVE TEST MODE' if client.is_configured else 'OFFLINE MOCK MODE'}"
    )

    # 1. Test Order Creation
    print_banner("1. Testing Order Creation (POST /v1/orders)")
    test_amount = 1499.00
    try:
        order = client.create_order(
            amount_rupees=test_amount,
            receipt="smoke_test_rcpt_001",
            notes={"source": "smoke_test", "customer_tier": "VIP"},
        )
        print("✓ Order Created Successfully!")
        print(f"  - Order ID: {order.get('id')}")
        print(f"  - Amount (Paise): {order.get('amount')} (₹{test_amount:,.2f})")
        print(f"  - Currency: {order.get('currency')}")
        print(f"  - Status: {order.get('status')}")
        print(f"  - Receipt: {order.get('receipt')}")
        print(f"  - Is Mock: {order.get('is_mock', False)}")
    except Exception as e:
        print(f"✗ Order Creation Failed: {e}")
        return

    # 2. Test Failure Reason Normalization Taxonomy
    print_banner("2. Testing Taxonomic Error Mapping")
    test_cases = [
        ("BAD_REQUEST_ERROR", "payment_cancelled", "Customer cancelled on checkout"),
        ("GATEWAY_ERROR", "bank_unavailable", "Bank network timeout"),
        ("BAD_REQUEST_ERROR", "payment_authentication_failed", "OTP verification failed"),
        ("BAD_REQUEST_ERROR", "card_expired", "Card expiry date invalid"),
        ("BAD_REQUEST_ERROR", "insufficient_funds", "Account balance insufficient"),
        ("BAD_REQUEST_ERROR", "amount_limit_exceeded", "Daily limit exceeded"),
    ]

    for err_code, err_reason, err_desc in test_cases:
        mapped_reason = client.normalize_failure_reason(err_code, err_reason, err_desc)
        print(f"  - [{err_code} | {err_reason}] -> FailureReason.{mapped_reason.value}")

    # 3. Test Webhook HMAC Signature Verification
    print_banner("3. Testing Webhook Cryptographic Verification")
    dummy_secret = "test_webhook_secret_key_123"
    sample_payload = json.dumps({"event": "payment.failed", "id": "evt_test_123"}).encode("utf-8")

    import hashlib
    import hmac

    valid_signature = hmac.new(dummy_secret.encode(), sample_payload, hashlib.sha256).hexdigest()
    invalid_signature = "invalid_signature_hex_12345"

    assert (
        client.verify_webhook_signature(sample_payload, valid_signature, secret=dummy_secret)
        is True
    )
    print("✓ Valid HMAC-SHA256 signature verified as TRUE")

    assert (
        client.verify_webhook_signature(sample_payload, invalid_signature, secret=dummy_secret)
        is False
    )
    print("✓ Tampered/invalid signature rejected as FALSE")

    print_banner("SUCCESS: ALL RAZORPAY SMOKE TESTS PASSED!")


if __name__ == "__main__":
    main()

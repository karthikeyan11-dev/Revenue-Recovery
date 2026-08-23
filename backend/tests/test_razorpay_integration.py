import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import Base, get_db
from app.integrations.razorpay_client import RazorpayClient
from app.main import app
from app.models.payment_failure import FailureReason
from app.models.recovery_case import RecoveryCase
from app.models.webhook_event import RazorpayWebhookEvent
from app.rag.playbook import RecoveryPlaybookService


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    # Seed ChromaDB playbook
    RecoveryPlaybookService.reset_playbook()
    for i in range(6):
        RecoveryPlaybookService.insert_resolved_case(
            case_id=f"seed_test_rzp_{i}",
            segment="REGULAR",
            failure_reason="INSUFFICIENT_FUNDS",
            action_taken="SEND_PAYMENT_LINK",
            channel="WHATSAPP",
            outcome="SUCCESS" if i < 4 else "FAILED",
            recovered_amount=2500.0,
        )
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
    RecoveryPlaybookService.reset_playbook()


@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_razorpay_client_offline_mock_mode():
    """Verify that when unconfigured, RazorpayClient generates a mock order ID without crashing."""
    client = RazorpayClient(key_id="", key_secret="")
    assert client.is_configured is False

    order = client.create_order(amount_rupees=2499.0, receipt="test_rcpt_001")
    assert order["id"].startswith("order_mock_")
    assert order["amount"] == 249900
    assert order["currency"] == "INR"
    assert order["is_mock"] is True


def test_razorpay_client_invalid_credentials_raises_error():
    """Verify that invalid configured credentials raise an error rather than silently masking."""
    client = RazorpayClient(key_id="rzp_test_INVALID_KEY", key_secret="INVALID_SECRET")
    assert client.is_configured is True

    with pytest.raises(ValueError, match="Razorpay API authentication failed"):
        client.create_order(amount_rupees=1000.0)


def test_razorpay_client_signature_verification():
    """Verify cryptographic HMAC-SHA256 signature verification logic."""
    client = RazorpayClient(webhook_secret="test_secret_12345")
    payload_bytes = b'{"event":"payment.failed","id":"evt_123"}'
    valid_sig = hmac.new(b"test_secret_12345", payload_bytes, hashlib.sha256).hexdigest()
    invalid_sig = "fake_signature_hash"

    assert (
        client.verify_webhook_signature(payload_bytes, valid_sig, secret="test_secret_12345")
        is True
    )
    assert (
        client.verify_webhook_signature(payload_bytes, invalid_sig, secret="test_secret_12345")
        is False
    )


def test_razorpay_failure_reason_taxonomy_mapping():
    """Verify mapping of real Razorpay error codes and reasons to FailureReason enum."""
    client = RazorpayClient()
    assert (
        client.normalize_failure_reason("BAD_REQUEST_ERROR", "insufficient_funds", "Low balance")
        == FailureReason.INSUFFICIENT_FUNDS
    )
    assert (
        client.normalize_failure_reason(
            "BAD_REQUEST_ERROR", "payment_cancelled", "User pressed back"
        )
        == FailureReason.USER_DROPOFF
    )
    assert (
        client.normalize_failure_reason(
            "GATEWAY_ERROR", "payment_authentication_failed", "OTP mismatch"
        )
        == FailureReason.AUTHENTICATION_FAILED
    )
    assert (
        client.normalize_failure_reason("BAD_REQUEST_ERROR", "card_expired", "Card expired")
        == FailureReason.EXPIRED_CARD
    )
    assert (
        client.normalize_failure_reason(
            "BAD_REQUEST_ERROR", "amount_limit_exceeded", "Limit reached"
        )
        == FailureReason.LIMIT_EXCEEDED
    )
    assert (
        client.normalize_failure_reason("GATEWAY_ERROR", "bank_unavailable", "Bank timeout")
        == FailureReason.NETWORK_ERROR
    )
    assert (
        client.normalize_failure_reason("BAD_REQUEST_ERROR", "unknown_decline", "Decline")
        == FailureReason.BANK_DECLINED
    )


def test_webhook_receiver_payment_failed_triggers_recovery_pipeline(client, test_db):
    """Verify that posting a payment.failed webhook event creates a PaymentFailure and executes recovery pipeline."""
    secret = settings.RAZORPAY_WEBHOOK_SECRET or "test_secret_for_unit_tests"
    payload = {
        "entity": "event",
        "account_id": "acc_test",
        "event": "payment.failed",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_failed_001",
                    "entity": "payment",
                    "amount": 350000,
                    "currency": "INR",
                    "status": "failed",
                    "order_id": "order_test_001",
                    "method": "upi",
                    "vpa": "failure@razorpay",
                    "email": "sunil.test@example.com",
                    "contact": "+919876543210",
                    "notes": {"customer_name": "Sunil Test"},
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_description": "Account balance insufficient.",
                    "error_source": "gateway",
                    "error_step": "payment_authorization",
                    "error_reason": "insufficient_funds",
                }
            }
        },
    }

    body_bytes = json.dumps(payload).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

    response = client.post(
        "/webhooks/razorpay",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
            "X-Razorpay-Event-Id": "evt_unit_test_001",
        },
    )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "processed"
    assert res_data["event_type"] == "payment.failed"
    assert res_data["case_id"] is not None

    # Verify case and webhook records in database
    case = test_db.query(RecoveryCase).filter(RecoveryCase.id == res_data["case_id"]).first()
    assert case is not None
    assert case.revenue_leak.amount == 3500.0

    wh_event = (
        test_db.query(RazorpayWebhookEvent)
        .filter(RazorpayWebhookEvent.event_id == "evt_unit_test_001")
        .first()
    )
    assert wh_event is not None
    assert wh_event.case_id == case.id


def test_webhook_receiver_idempotency(client, test_db):
    """Verify that posting the same event ID twice returns already_processed without duplicate work."""
    secret = settings.RAZORPAY_WEBHOOK_SECRET or "test_secret_for_unit_tests"
    payload = {
        "entity": "event",
        "event": "payment.captured",
        "id": "evt_idempotent_test_001",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_captured_001",
                    "amount": 250000,
                    "status": "captured",
                }
            }
        },
    }

    body_bytes = json.dumps(payload).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
        "X-Razorpay-Event-Id": "evt_idempotent_test_001",
    }

    # First Call: Processed
    resp1 = client.post("/webhooks/razorpay", content=body_bytes, headers=headers)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "processed"

    # Second Call: Already Processed (Idempotent)
    resp2 = client.post("/webhooks/razorpay", content=body_bytes, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "already_processed"

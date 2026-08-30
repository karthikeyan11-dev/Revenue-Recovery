import hashlib
import hmac
import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.integrations.razorpay.client import RazorpayClient
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService
from app.main import app
from app.models.customer import Customer
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.promise_to_pay import PromiseStatus, PromiseToPay
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import LeakType, RevenueLeak
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.models.webhook_event import RazorpayWebhookEvent


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


def test_razorpay_client_invalid_credentials_raises_error(monkeypatch):
    """Verify that invalid configured credentials raise an error rather than silently masking."""
    client = RazorpayClient(key_id="rzp_test_INVALID_KEY", key_secret="INVALID_SECRET")
    assert client.is_configured is True

    import httpx

    class Mock401Response:
        status_code = 401
        text = '{"error": {"description": "Invalid key or secret"}}'

    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: Mock401Response())

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


def test_webhook_receiver_invalid_signature_rejected(client):
    """Verify that an invalid HMAC signature is immediately rejected with HTTP 400."""
    payload = {"event": "payment.failed", "id": "evt_invalid_sig"}
    body_bytes = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/razorpay",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": "invalid_signature_digest_12345",
            "X-Razorpay-Event-Id": "evt_invalid_sig",
        },
    )
    assert response.status_code == 400
    assert "Invalid webhook signature" in response.json()["detail"]


def test_webhook_receiver_payment_failed_triggers_recovery_pipeline(client, test_db):
    """Verify that posting payment.failed returns fast 200 accepted and executes recovery pipeline."""
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
    assert res_data["status"] == "accepted"
    assert res_data["event_type"] == "payment.failed"
    assert res_data["failure_id"] is not None

    # Verify PaymentFailure persisted with forensics
    failure = (
        test_db.query(PaymentFailure).filter(PaymentFailure.id == res_data["failure_id"]).first()
    )
    assert failure is not None
    assert failure.raw_error_reason == "insufficient_funds"
    assert failure.razorpay_payment_id == "pay_test_failed_001"

    # Verify Webhook Event persisted
    wh_event = (
        test_db.query(RazorpayWebhookEvent)
        .filter(RazorpayWebhookEvent.event_id == "evt_unit_test_001")
        .first()
    )
    assert wh_event is not None


def test_webhook_receiver_payment_captured_closes_active_case(client, test_db):
    """Verify that posting payment.captured resolves an open/in_progress case and marks transaction SUCCESS."""
    secret = settings.RAZORPAY_WEBHOOK_SECRET or "test_secret_for_unit_tests"

    # 1. Setup Customer, Transaction, Failure, Leak, and Active Recovery Case with Promise
    cust = Customer(
        id="cust_captured_01",
        name="Pooja Test",
        email="pooja.test@example.com",
        phone="+919845012345",
    )
    test_db.add(cust)

    tx = Transaction(
        id="txn_captured_01",
        customer_id=cust.id,
        amount=4500.0,
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.CARD,
        razorpay_order_id="order_captured_001",
        created_at=datetime.utcnow(),
    )
    test_db.add(tx)

    pf = PaymentFailure(
        id="pf_captured_01",
        transaction_id=tx.id,
        failure_reason=FailureReason.AUTHENTICATION_FAILED,
        raw_error_code="GATEWAY_ERROR",
        raw_error_message="OTP failed",
        attempt_number=1,
        created_at=datetime.utcnow(),
    )
    test_db.add(pf)

    leak = RevenueLeak(
        id="leak_captured_01",
        failure_id=pf.id,
        leak_type=LeakType.TRANSACTION_FAILURE,
        amount=4500.0,
        confidence=0.90,
        recoverability_score=0.85,
    )
    test_db.add(leak)

    case = RecoveryCase(
        id="case_captured_01",
        leak_id=leak.id,
        customer_id=cust.id,
        status=CaseStatus.IN_PROGRESS,
        recovered_amount=0.0,
        created_at=datetime.utcnow(),
    )
    test_db.add(case)

    promise = PromiseToPay(
        id="ptp_captured_01",
        case_id=case.id,
        committed_amount=4500.0,
        committed_date=datetime.utcnow(),
        status=PromiseStatus.PENDING,
        follow_up_count=0,
        created_at=datetime.utcnow(),
    )
    test_db.add(promise)
    test_db.commit()

    # 2. Post payment.captured event
    payload = {
        "entity": "event",
        "event": "payment.captured",
        "id": "evt_captured_001",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_captured_001",
                    "amount": 450000,
                    "status": "captured",
                    "order_id": "order_captured_001",
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
            "X-Razorpay-Event-Id": "evt_captured_001",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processed"

    # 3. Assert Database state: Transaction is SUCCESS, Case is RECOVERED, Promise is KEPT
    test_db.refresh(tx)
    test_db.refresh(case)
    test_db.refresh(promise)

    assert tx.status == TransactionStatus.SUCCESS
    assert case.status == CaseStatus.RECOVERED
    assert case.recovered_amount == 4500.0
    assert case.resolved_at is not None
    assert promise.status == PromiseStatus.KEPT
    assert promise.resolved_at is not None


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

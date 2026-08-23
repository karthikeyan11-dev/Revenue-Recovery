import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.integrations.razorpay_client import RazorpayClient
from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import PaymentFailure
from app.models.recovery_case import CaseStatus
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.models.webhook_event import RazorpayWebhookEvent
from app.services.recovery_service import RecoveryService

logger = logging.getLogger("app.api.webhooks")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/razorpay",
    summary="Razorpay Webhook Receiver",
    operation_id="handle_razorpay_webhook",
)
async def handle_razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_razorpay_signature: str | None = Header(default=None, alias="X-Razorpay-Signature"),
    x_razorpay_event_id: str | None = Header(default=None, alias="X-Razorpay-Event-Id"),
) -> dict:
    """
    Receives, verifies, and processes authentic Razorpay webhook events.
    - Validates HMAC-SHA256 signature against raw request body bytes.
    - Idempotently prevents duplicate executions using event ID.
    - Persists raw webhook payload for audit and forensics.
    - When payment.failed occurs: creates PaymentFailure and triggers LangGraph Recovery Pipeline.
    """
    # 1. Read Raw Body Bytes for Cryptographic Signature Verification
    body_bytes = await request.body()
    if not body_bytes:
        raise HTTPException(status_code=400, detail="Empty webhook payload")

    # 2. Verify HMAC-SHA256 Signature if webhook secret is configured
    rzp_client = RazorpayClient()
    if settings.RAZORPAY_WEBHOOK_SECRET:
        if not x_razorpay_signature:
            logger.warning("[Webhook:Razorpay] Missing X-Razorpay-Signature header.")
            raise HTTPException(status_code=400, detail="Missing X-Razorpay-Signature header")

        is_valid = rzp_client.verify_webhook_signature(
            body_bytes=body_bytes,
            signature=x_razorpay_signature,
        )
        if not is_valid:
            logger.error("[Webhook:Razorpay] Invalid webhook signature.")
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # 3. Parse JSON Payload
    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"[Webhook:Razorpay] Invalid JSON body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from e

    event_id = x_razorpay_event_id or payload.get("id") or f"evt_{uuid.uuid4().hex[:14]}"
    event_type = payload.get("event", "unknown")
    logger.info(f"[Webhook:Razorpay] Received event '{event_type}' (ID: {event_id})")

    # 4. Idempotency Check
    existing_event = (
        db.query(RazorpayWebhookEvent).filter(RazorpayWebhookEvent.event_id == event_id).first()
    )
    if existing_event:
        logger.info(
            f"[Webhook:Razorpay] Event {event_id} already processed. Skipping duplicate execution."
        )
        return {
            "status": "already_processed",
            "event_id": event_id,
            "event_type": event_type,
        }

    # 5. Persist Raw Webhook Record for Auditing & Forensics
    webhook_record = RazorpayWebhookEvent(
        id=f"wh_{uuid.uuid4().hex[:14]}",
        event_id=event_id,
        event_type=event_type,
        signature=x_razorpay_signature,
        payload_json=body_bytes.decode("utf-8"),
        processed=True,
        created_at=datetime.utcnow(),
    )
    db.add(webhook_record)
    db.commit()

    # 6. Event Handling & Convergence into Recovery Pipeline
    if event_type == "payment.failed":
        pay_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        payment_id = pay_entity.get("id", f"pay_{uuid.uuid4().hex[:14]}")
        order_id = pay_entity.get("order_id")
        amount_rupees = float(pay_entity.get("amount", 0.0)) / 100.0
        currency = pay_entity.get("currency", "INR")
        contact = pay_entity.get("contact", "+919876543210")
        email = pay_entity.get("email", "customer@example.com")
        method_str = pay_entity.get("method", "card").upper()
        notes = pay_entity.get("notes", {})

        # Extract Authentic Razorpay Error Forensics
        error_code = pay_entity.get("error_code")
        error_desc = pay_entity.get("error_description")
        error_source = pay_entity.get("error_source", "gateway")
        error_step = pay_entity.get("error_step", "payment_authorization")
        error_reason = pay_entity.get("error_reason")

        # Map to internal FailureReason taxonomy
        failure_reason = rzp_client.normalize_failure_reason(
            error_code=error_code,
            error_reason=error_reason,
            error_description=error_desc,
        )

        logger.info(
            f"[Webhook:Razorpay] Processing failed payment {payment_id} | Reason: {failure_reason.value} | "
            f"Raw Error: {error_code} / {error_reason}"
        )

        # Look up or create Customer
        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            customer = Customer(
                id=f"cust_{uuid.uuid4().hex[:12]}",
                name=notes.get("customer_name", "Valued Customer"),
                email=email,
                phone=contact,
                segment=CustomerSegment.REGULAR,
                ltv=max(15000.0, amount_rupees * 3),
                churn_probability=0.20,
                preferred_channel=CommunicationChannel.WHATSAPP,
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)

        # Look up or create Transaction
        transaction = (
            db.query(Transaction)
            .filter(
                (Transaction.razorpay_order_id == order_id)
                | (Transaction.id == notes.get("transaction_id"))
            )
            .first()
            if order_id
            else None
        )

        if not transaction:
            try:
                pay_method = PaymentMethod[method_str]
            except KeyError:
                pay_method = PaymentMethod.CARD

            transaction = Transaction(
                id=f"txn_{uuid.uuid4().hex[:14]}",
                customer_id=customer.id,
                amount=amount_rupees,
                currency=currency,
                status=TransactionStatus.FAILED,
                payment_method=pay_method,
                razorpay_order_id=order_id,
                created_at=datetime.utcnow(),
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
        else:
            transaction.status = TransactionStatus.FAILED
            db.commit()

        # Create PaymentFailure Record preserving full error forensics
        failure = PaymentFailure(
            id=f"fail_{uuid.uuid4().hex[:14]}",
            transaction_id=transaction.id,
            failure_reason=failure_reason,
            raw_error_code=error_code or f"ERR_{failure_reason.value[:8]}",
            raw_error_message=error_desc or f"Razorpay failure: {error_reason}",
            raw_error_source=error_source,
            raw_error_step=error_step,
            raw_error_reason=error_reason,
            razorpay_payment_id=payment_id,
            attempt_number=1,
            created_at=datetime.utcnow(),
        )
        db.add(failure)
        db.commit()
        db.refresh(failure)

        # Trigger Autonomous LangGraph Recovery Pipeline
        recovery_service = RecoveryService(db)
        case = recovery_service.process_single_failure_pipeline(failure, use_mock=False)

        # Link case ID to webhook event record
        webhook_record.case_id = case.id
        db.commit()

        logger.info(
            f"[Webhook:Razorpay] Autonomous recovery pipeline executed for payment {payment_id} -> Case {case.id} (Status: {case.status.value})"
        )

        return {
            "status": "processed",
            "event_type": "payment.failed",
            "event_id": event_id,
            "case_id": case.id,
            "case_status": case.status.value,
            "payment_id": payment_id,
            "failure_reason": failure_reason.value,
        }

    elif event_type in ("payment.captured", "order.paid"):
        pay_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = pay_entity.get("order_id")

        if order_id:
            tx = db.query(Transaction).filter(Transaction.razorpay_order_id == order_id).first()
            if tx:
                tx.status = TransactionStatus.SUCCESS
                # Resolve associated case if open
                for pf in tx.payment_failures:
                    for leak in pf.revenue_leaks:
                        if leak.recovery_case and leak.recovery_case.status in (
                            CaseStatus.OPEN,
                            CaseStatus.IN_PROGRESS,
                        ):
                            leak.recovery_case.status = CaseStatus.RECOVERED
                            leak.recovery_case.recovered_amount = tx.amount
                            leak.recovery_case.resolved_at = datetime.utcnow()
                db.commit()

        return {
            "status": "processed",
            "event_type": event_type,
            "event_id": event_id,
        }

    return {
        "status": "ignored",
        "event_type": event_type,
        "event_id": event_id,
    }

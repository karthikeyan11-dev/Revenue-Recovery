import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.integrations.razorpay.client import RazorpayClient
from app.models.customer import Customer
from app.models.payment_failure import PaymentFailure
from app.models.promise_to_pay import PromiseStatus
from app.models.recovery_case import CaseStatus, RecoveryCase
from app.models.revenue_leak import RevenueLeak
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.models.webhook_event import RazorpayWebhookEvent
from app.services.recovery_orchestrator import RecoveryOrchestratorService

logger = logging.getLogger("app.api.routes.webhook")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def run_background_recovery(failure_id: str, webhook_event_id: str) -> None:
    """
    Background worker task: Executes the compiled LangGraph recovery workflow
    (Detective -> Intel -> Strategist -> Policy -> Executor -> Analyst)
    asynchronously without blocking the HTTP webhook acknowledgement.
    """
    db = SessionLocal()
    try:
        failure = db.query(PaymentFailure).filter(PaymentFailure.id == failure_id).first()
        if not failure:
            logger.warning(f"[Webhook:Background] PaymentFailure {failure_id} not found.")
            return

        tx = failure.transaction
        if tx and tx.status == TransactionStatus.SUCCESS:
            logger.info(
                f"[Webhook:Background] Transaction {tx.id} already marked SUCCESS. Skipping recovery."
            )
            return

        # Check if an existing case for this failure is already in a terminal status
        existing_case = (
            db.query(RecoveryCase)
            .join(RevenueLeak)
            .filter(RevenueLeak.failure_id == failure.id)
            .first()
        )
        if existing_case and existing_case.status in (
            CaseStatus.RECOVERED,
            CaseStatus.ESCALATED,
            CaseStatus.BLOCKED,
        ):
            logger.info(
                f"[Webhook:Background] Case {existing_case.id} already in terminal status {existing_case.status.value}. Skipping duplicate execution."
            )
            return

        recovery_service = RecoveryOrchestratorService(db)
        case = recovery_service.process_single_failure_pipeline(failure, use_mock=False)

        wh_event = (
            db.query(RazorpayWebhookEvent)
            .filter(RazorpayWebhookEvent.id == webhook_event_id)
            .first()
        )
        if wh_event:
            wh_event.case_id = case.id
            db.commit()

        logger.info(
            f"[Webhook:Background] Autonomous recovery pipeline completed for payment failure {failure_id} -> Case {case.id} (Status: {case.status.value})"
        )
    except Exception as e:
        logger.exception(
            f"[Webhook:Background] Error executing autonomous recovery workflow for failure {failure_id}: {e}"
        )
    finally:
        db.close()


@router.post(
    "/razorpay",
    summary="Razorpay Webhook Receiver",
    operation_id="handle_razorpay_webhook",
)
async def handle_razorpay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_razorpay_signature: str | None = Header(default=None, alias="X-Razorpay-Signature"),
    x_razorpay_event_id: str | None = Header(default=None, alias="X-Razorpay-Event-Id"),
) -> dict:
    """
    Receives, cryptographically validates, and processes authentic Razorpay webhook events.
    - Validates HMAC-SHA256 signature against raw request body bytes.
    - Idempotently prevents duplicate executions using event ID.
    - Persists raw webhook payload for audit and forensics.
    - Quickly acknowledges webhook (HTTP 200) and schedules LangGraph recovery in background.
    - For payment.captured: closes active recovery cases and marks transaction SUCCESS.
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

    # 6. Event Handling
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
            f"[Webhook:Razorpay] Ingesting failed payment {payment_id} | Reason: {failure_reason.value} | "
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

        # Create or reuse PaymentFailure Record preserving full error forensics
        failure = (
            db.query(PaymentFailure)
            .filter(PaymentFailure.razorpay_payment_id == payment_id)
            .first()
            if payment_id
            else None
        )
        if not failure:
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

        # Schedule autonomous LangGraph recovery workflow as a background task
        background_tasks.add_task(run_background_recovery, failure.id, webhook_record.id)

        logger.info(
            f"[Webhook:Razorpay] Scheduled background recovery workflow for failure {failure.id} (Payment: {payment_id})"
        )

        return {
            "status": "accepted",
            "event_type": "payment.failed",
            "event_id": event_id,
            "payment_id": payment_id,
            "failure_id": failure.id,
            "failure_reason": failure_reason.value,
        }

    elif event_type in ("payment.captured", "order.paid"):
        pay_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = pay_entity.get("order_id")
        amount_rupees = float(pay_entity.get("amount", 0.0)) / 100.0

        if order_id:
            tx = db.query(Transaction).filter(Transaction.razorpay_order_id == order_id).first()
            if tx:
                tx.status = TransactionStatus.SUCCESS
                # Resolve any associated active recovery case
                for pf in tx.payment_failures:
                    for leak in pf.revenue_leaks:
                        if leak.recovery_case and leak.recovery_case.status in (
                            CaseStatus.OPEN,
                            CaseStatus.IN_PROGRESS,
                        ):
                            leak.recovery_case.status = CaseStatus.RECOVERED
                            leak.recovery_case.recovered_amount = (
                                amount_rupees if amount_rupees > 0 else tx.amount
                            )
                            leak.recovery_case.resolved_at = datetime.utcnow()
                            webhook_record.case_id = leak.recovery_case.id

                            # Also resolve any pending promises-to-pay
                            for promise in leak.recovery_case.promises_to_pay:
                                if promise.status == PromiseStatus.PENDING:
                                    promise.status = PromiseStatus.KEPT
                                    promise.resolved_at = datetime.utcnow()

                db.commit()
                logger.info(
                    f"[Webhook:Razorpay] Resolved active recovery cases for captured order {order_id} -> SUCCESS"
                )

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

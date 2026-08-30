import logging
import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.integrations.razorpay.client import RazorpayClient
from app.models.audit_log import AuditLog
from app.models.communication_event import CommunicationEvent
from app.models.customer import Customer
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.promise_to_pay import PromiseToPay
from app.models.recovery_action import RecoveryAction
from app.models.recovery_case import RecoveryCase
from app.models.recovery_metrics import RecoveryMetricsRecord
from app.models.revenue_leak import RevenueLeak
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.models.webhook_event import RazorpayWebhookEvent
from app.repositories.customer import CustomerRepository
from app.repositories.transaction import TransactionRepository

logger = logging.getLogger("app.generators.synthetic")

FIRST_NAMES = [
    "Aarav",
    "Vivaan",
    "Aditya",
    "Vihaan",
    "Arjun",
    "Sai",
    "Reyansh",
    "Ayaan",
    "Krishna",
    "Ishaan",
    "Shaurya",
    "Atharva",
    "Advik",
    "Pranav",
    "Advaith",
    "Aanya",
    "Diya",
    "Saanvi",
    "Ananya",
    "Aadhya",
    "Pari",
    "Chiara",
    "Myra",
    "Riya",
    "Isha",
    "Kavya",
    "Anika",
    "Navya",
    "Sneha",
    "Tanvi",
    "Pooja",
    "Rahul",
    "Rohan",
    "Vikram",
    "Siddharth",
    "Karthik",
    "Manish",
    "Amit",
    "Dev",
]

LAST_NAMES = [
    "Sharma",
    "Verma",
    "Patel",
    "Mehta",
    "Gupta",
    "Singh",
    "Kumar",
    "Rao",
    "Nair",
    "Iyer",
    "Reddy",
    "Chopra",
    "Joshi",
    "Bhat",
    "Deshmukh",
    "Kulkarni",
    "Agarwal",
    "Banerjee",
    "Chatterjee",
    "Mukherjee",
    "Sen",
    "Bose",
    "Dutta",
]


class SyntheticDataGenerator:
    """
    Generates realistic Indian e-commerce / subscription transaction dataset.
    """

    @classmethod
    def generate_customers(cls, count: int = 150) -> list[Customer]:
        customers = []

        for _idx in range(count):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}{random.randint(10, 999)}@example.com"
            # 90% have phone numbers, 10% email only to test factual channel availability
            phone = f"+9198{random.randint(10000000, 99999999)}" if random.random() < 0.90 else None

            customers.append(
                Customer(
                    id=f"cust_{uuid.uuid4().hex[:12]}",
                    name=name,
                    email=email,
                    phone=phone,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                )
            )
        return customers

    @classmethod
    def generate_transactions(
        cls,
        customers: list[Customer],
        total_count: int = 500,
        failure_rate: float = 0.25,
        real_razorpay_orders_count: int = 0,
    ) -> tuple[list[Transaction], list[PaymentFailure]]:
        transactions = []
        failures = []

        failure_reasons = [
            (FailureReason.BANK_DECLINED, 0.30),
            (FailureReason.INSUFFICIENT_FUNDS, 0.25),
            (FailureReason.NETWORK_ERROR, 0.20),
            (FailureReason.AUTHENTICATION_FAILED, 0.12),
            (FailureReason.USER_DROPOFF, 0.08),
            (FailureReason.EXPIRED_CARD, 0.05),
        ]

        now = datetime.utcnow()
        rzp_client = RazorpayClient()

        for idx in range(total_count):
            customer = random.choice(customers)

            # Continuous transaction amount distribution
            amount = random.choices(
                [
                    random.uniform(499.0, 2500.0),
                    random.uniform(2500.0, 9999.0),
                    random.uniform(10000.0, 45000.0),
                ],
                weights=[0.60, 0.30, 0.10],
            )[0]

            is_failed = random.random() < failure_rate
            status = TransactionStatus.FAILED if is_failed else TransactionStatus.SUCCESS
            created_time = now - timedelta(
                days=random.randint(0, 14),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            if idx < real_razorpay_orders_count and rzp_client.is_configured:
                try:
                    rzp_order = rzp_client.create_order(
                        amount_rupees=round(amount, 2),
                        receipt=f"rcpt_hero_{idx+1}",
                        notes={"customer_id": customer.id},
                    )
                    order_id = rzp_order.get("id", f"order_{uuid.uuid4().hex[:14]}")
                except Exception as e:
                    logger.warning(f"Failed to create live Razorpay order for hero tx #{idx}: {e}")
                    order_id = f"order_{uuid.uuid4().hex[:14]}"
            else:
                order_id = f"order_{uuid.uuid4().hex[:14]}"

            tx = Transaction(
                id=f"txn_{uuid.uuid4().hex[:14]}",
                customer_id=customer.id,
                amount=round(amount, 2),
                currency="INR",
                status=status,
                payment_method=random.choices(
                    [PaymentMethod.UPI, PaymentMethod.CARD, PaymentMethod.NETBANKING],
                    weights=[0.55, 0.35, 0.10],
                )[0],
                checkout_session_id=f"cs_{uuid.uuid4().hex[:16]}",
                razorpay_order_id=order_id,
                created_at=created_time,
            )
            transactions.append(tx)

            if is_failed:
                r = random.random()
                cum = 0.0
                reason = FailureReason.BANK_DECLINED
                for f_reason, weight in failure_reasons:
                    cum += weight
                    if r <= cum:
                        reason = f_reason
                        break

                failure = PaymentFailure(
                    id=f"fail_{uuid.uuid4().hex[:14]}",
                    transaction_id=tx.id,
                    failure_reason=reason,
                    raw_error_code=f"ERR_{reason.value[:8]}",
                    raw_error_message=f"Issuer response: {reason.value.replace('_', ' ')}",
                    raw_error_source="issuer",
                    raw_error_step="payment_authorization",
                    raw_error_reason=reason.value.lower(),
                    razorpay_payment_id=f"pay_{uuid.uuid4().hex[:14]}",
                    attempt_number=random.choices([1, 2, 3, 4], weights=[0.72, 0.18, 0.07, 0.03])[
                        0
                    ],
                    created_at=created_time + timedelta(seconds=random.randint(5, 30)),
                )
                failures.append(failure)

        return transactions, failures

    @classmethod
    def reset_postgres_data(cls, db: Session) -> dict:
        """
        Truncates Postgres tables specifically (preserving ChromaDB recovery_playbook collection).
        """
        logger.info("Resetting Postgres transaction, failure, and recovery data...")
        bind = db.get_bind()
        if bind.dialect.name == "postgresql":
            db.execute(
                text(
                    """
                    TRUNCATE TABLE
                        recovery_actions,
                        communication_events,
                        promise_to_pay,
                        audit_logs,
                        recovery_cases,
                        revenue_leaks,
                        payment_failures,
                        transactions,
                        customers,
                        recovery_metrics,
                        razorpay_webhook_events
                    RESTART IDENTITY CASCADE;
                    """
                )
            )
            db.commit()
        else:
            for model in [
                RecoveryAction,
                CommunicationEvent,
                PromiseToPay,
                AuditLog,
                RecoveryCase,
                RevenueLeak,
                PaymentFailure,
                Transaction,
                Customer,
                RecoveryMetricsRecord,
                RazorpayWebhookEvent,
            ]:
                db.query(model).delete()
            db.commit()
        return {"status": "success", "message": "Postgres data reset cleanly."}

    @classmethod
    def seed_playbook_precedents(cls) -> int:
        """
        Seeds foundational historical resolved cases into ChromaDB recovery_playbook
        to ensure sufficient precedent evidence for all failure categories.
        """
        precedents = [
            # NETWORK_ERROR
            ("hist_net_1", "NETWORK_ERROR", "RETRY", "NONE", "SUCCESS", 2400.0),
            ("hist_net_2", "NETWORK_ERROR", "RETRY", "NONE", "SUCCESS", 5200.0),
            ("hist_net_3", "NETWORK_ERROR", "RETRY", "NONE", "SUCCESS", 1800.0),
            ("hist_net_4", "NETWORK_ERROR", "RETRY", "NONE", "SUCCESS", 3100.0),
            ("hist_net_5", "NETWORK_ERROR", "RETRY", "NONE", "FAILED", 0.0),
            ("hist_net_6", "NETWORK_ERROR", "RETRY", "NONE", "SUCCESS", 4500.0),
            # INSUFFICIENT_FUNDS
            ("hist_ins_1", "INSUFFICIENT_FUNDS", "RETRY", "NONE", "SUCCESS", 8500.0),
            ("hist_ins_2", "INSUFFICIENT_FUNDS", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 3200.0),
            ("hist_ins_3", "INSUFFICIENT_FUNDS", "RETRY", "NONE", "SUCCESS", 12000.0),
            (
                "hist_ins_4",
                "INSUFFICIENT_FUNDS",
                "SEND_PAYMENT_LINK",
                "WHATSAPP",
                "SUCCESS",
                4100.0,
            ),
            ("hist_ins_5", "INSUFFICIENT_FUNDS", "RETRY", "NONE", "SUCCESS", 9500.0),
            ("hist_ins_6", "INSUFFICIENT_FUNDS", "RETRY", "NONE", "FAILED", 0.0),
            # USER_DROPOFF
            ("hist_drp_1", "USER_DROPOFF", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 2999.0),
            ("hist_drp_2", "USER_DROPOFF", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 6400.0),
            ("hist_drp_3", "USER_DROPOFF", "OFFER_INCENTIVE", "WHATSAPP", "SUCCESS", 1500.0),
            ("hist_drp_4", "USER_DROPOFF", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 4200.0),
            ("hist_drp_5", "USER_DROPOFF", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 8900.0),
            ("hist_drp_6", "USER_DROPOFF", "SEND_WHATSAPP", "WHATSAPP", "FAILED", 0.0),
            # EXPIRED_CARD
            ("hist_exp_1", "EXPIRED_CARD", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 3500.0),
            ("hist_exp_2", "EXPIRED_CARD", "SEND_PAYMENT_LINK", "EMAIL", "SUCCESS", 4900.0),
            ("hist_exp_3", "EXPIRED_CARD", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 7800.0),
            ("hist_exp_4", "EXPIRED_CARD", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 2200.0),
            ("hist_exp_5", "EXPIRED_CARD", "SEND_PAYMENT_LINK", "EMAIL", "FAILED", 0.0),
            ("hist_exp_6", "EXPIRED_CARD", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 6100.0),
            # BANK_DECLINED
            ("hist_bnk_1", "BANK_DECLINED", "RETRY", "NONE", "SUCCESS", 4200.0),
            ("hist_bnk_2", "BANK_DECLINED", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 5600.0),
            ("hist_bnk_3", "BANK_DECLINED", "RETRY", "NONE", "SUCCESS", 3100.0),
            ("hist_bnk_4", "BANK_DECLINED", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 8900.0),
            ("hist_bnk_5", "BANK_DECLINED", "RETRY", "NONE", "FAILED", 0.0),
            ("hist_bnk_6", "BANK_DECLINED", "RETRY", "NONE", "SUCCESS", 2800.0),
            # AUTHENTICATION_FAILED
            ("hist_ath_1", "AUTHENTICATION_FAILED", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 3900.0),
            ("hist_ath_2", "AUTHENTICATION_FAILED", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 7200.0),
            (
                "hist_ath_3",
                "AUTHENTICATION_FAILED",
                "SEND_PAYMENT_LINK",
                "WHATSAPP",
                "SUCCESS",
                2100.0,
            ),
            ("hist_ath_4", "AUTHENTICATION_FAILED", "SEND_WHATSAPP", "WHATSAPP", "SUCCESS", 5400.0),
            ("hist_ath_5", "AUTHENTICATION_FAILED", "SEND_WHATSAPP", "WHATSAPP", "FAILED", 0.0),
            # LIMIT_EXCEEDED
            ("hist_lmt_1", "LIMIT_EXCEEDED", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 12000.0),
            ("hist_lmt_2", "LIMIT_EXCEEDED", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 18500.0),
            ("hist_lmt_3", "LIMIT_EXCEEDED", "SEND_PAYMENT_LINK", "EMAIL", "SUCCESS", 9500.0),
            ("hist_lmt_4", "LIMIT_EXCEEDED", "SEND_PAYMENT_LINK", "WHATSAPP", "SUCCESS", 15000.0),
            ("hist_lmt_5", "LIMIT_EXCEEDED", "SEND_PAYMENT_LINK", "WHATSAPP", "FAILED", 0.0),
        ]
        try:
            from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService

            for cid, reason, action, chan, outc, rec_amt in precedents:
                RecoveryPlaybookService.insert_resolved_case(
                    case_id=cid,
                    failure_reason=reason,
                    action_taken=action,
                    channel=chan,
                    outcome=outc,
                    recovered_amount=rec_amt,
                )
            logger.info(f"Seeded {len(precedents)} historical precedents in ChromaDB playbook.")
            return len(precedents)
        except Exception as e:
            logger.warning(f"Could not seed ChromaDB playbook precedents: {e}")
            return 0

    @classmethod
    def populate_database(
        cls,
        db: Session,
        customer_count: int = 150,
        transaction_count: int = 500,
        failure_rate: float = 0.25,
        real_razorpay_orders_count: int = 0,
        clear_existing: bool = True,
    ) -> dict:
        cust_repo = CustomerRepository(db)
        txn_repo = TransactionRepository(db)

        # Clear existing data if requested (default True to prevent uncontrolled growth)
        if clear_existing:
            cls.reset_postgres_data(db)

        logger.info("Generating synthetic cohorts...")
        customers = cls.generate_customers(customer_count)
        cust_repo.bulk_create(customers)

        transactions, failures = cls.generate_transactions(
            customers,
            total_count=transaction_count,
            failure_rate=failure_rate,
            real_razorpay_orders_count=real_razorpay_orders_count,
        )
        txn_repo.bulk_create(transactions)
        txn_repo.bulk_create_failures(failures)

        # Seed initial RAG playbook precedent cases
        cls.seed_playbook_precedents()

        logger.info(
            f"Successfully seeded {len(customers)} customers, {len(transactions)} transactions, and {len(failures)} failures."
        )

        return {
            "status": "success",
            "customers_generated": len(customers),
            "transactions_generated": len(transactions),
            "failures_generated": len(failures),
            "message": f"Generated {len(transactions)} transactions with {len(failures)} failure states.",
        }

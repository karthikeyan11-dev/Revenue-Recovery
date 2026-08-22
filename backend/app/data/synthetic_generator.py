import logging
import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.transaction import PaymentMethod, Transaction, TransactionStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.transaction_repository import TransactionRepository

logger = logging.getLogger("app.data.synthetic_generator")

FIRST_NAMES = [
    "Aarav",
    "Aditi",
    "Ananya",
    "Dev",
    "Diya",
    "Ishaan",
    "Kavya",
    "Manish",
    "Neha",
    "Pranav",
    "Pooja",
    "Rahul",
    "Rhea",
    "Rohan",
    "Sanjay",
    "Shreya",
    "Tanvi",
    "Varun",
    "Vikram",
    "Zoya",
    "Arjun",
    "Deepak",
    "Gaurav",
    "Kiran",
]

LAST_NAMES = [
    "Sharma",
    "Verma",
    "Patel",
    "Reddy",
    "Mehta",
    "Iyer",
    "Nair",
    "Chopra",
    "Kapoor",
    "Joshi",
    "Bhatia",
    "Sen",
    "Deshmukh",
    "Singhania",
    "Rao",
    "Gupta",
]


class SyntheticDataGenerator:
    """
    Generates realistic Indian e-commerce / subscription transaction dataset.
    """

    @classmethod
    def generate_customers(cls, count: int = 150) -> list[Customer]:
        customers = []
        segments = [
            (CustomerSegment.HIGH_VALUE, 0.15),
            (CustomerSegment.LOYAL, 0.20),
            (CustomerSegment.REGULAR, 0.35),
            (CustomerSegment.AT_RISK, 0.15),
            (CustomerSegment.CHURNING, 0.10),
            (CustomerSegment.LOW_VALUE, 0.05),
        ]

        for _ in range(count):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}{random.randint(10, 999)}@example.com"
            phone = f"+9198{random.randint(10000000, 99999999)}"

            # Segment selection
            r = random.random()
            cum = 0.0
            chosen_segment = CustomerSegment.REGULAR
            for seg, weight in segments:
                cum += weight
                if r <= cum:
                    chosen_segment = seg
                    break

            # LTV & Churn risk based on segment
            if chosen_segment == CustomerSegment.HIGH_VALUE:
                ltv = random.uniform(30000.0, 150000.0)
                churn_prob = random.uniform(0.05, 0.25)
            elif chosen_segment == CustomerSegment.LOYAL:
                ltv = random.uniform(15000.0, 50000.0)
                churn_prob = random.uniform(0.02, 0.15)
            elif chosen_segment == CustomerSegment.AT_RISK:
                ltv = random.uniform(8000.0, 30000.0)
                churn_prob = random.uniform(0.40, 0.75)
            elif chosen_segment == CustomerSegment.CHURNING:
                ltv = random.uniform(5000.0, 25000.0)
                churn_prob = random.uniform(0.70, 0.95)
            else:
                ltv = random.uniform(1500.0, 12000.0)
                churn_prob = random.uniform(0.10, 0.40)

            channel = random.choices(
                [
                    CommunicationChannel.WHATSAPP,
                    CommunicationChannel.EMAIL,
                    CommunicationChannel.SMS,
                ],
                weights=[0.60, 0.30, 0.10],
            )[0]

            customer = Customer(
                id=f"cust_{uuid.uuid4().hex[:12]}",
                name=f"{first} {last}",
                email=email,
                phone=phone,
                segment=chosen_segment,
                ltv=round(ltv, 2),
                churn_probability=round(churn_prob, 2),
                preferred_channel=channel,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
            )
            customers.append(customer)

        return customers

    @classmethod
    def generate_transactions(
        cls,
        customers: list[Customer],
        total_count: int = 500,
        failure_rate: float = 0.25,
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

        for _ in range(total_count):
            customer = random.choice(customers)

            # Amount distribution skewed towards typical orders with some high value
            if customer.segment == CustomerSegment.HIGH_VALUE:
                amount = random.uniform(8000.0, 85000.0)
            else:
                amount = random.choices(
                    [
                        random.uniform(499.0, 2500.0),
                        random.uniform(2500.0, 9999.0),
                        random.uniform(10000.0, 35000.0),
                    ],
                    weights=[0.65, 0.25, 0.10],
                )[0]

            is_failed = random.random() < failure_rate
            status = TransactionStatus.FAILED if is_failed else TransactionStatus.SUCCESS
            created_time = now - timedelta(
                days=random.randint(0, 14),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

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
                created_at=created_time,
            )
            transactions.append(tx)

            if is_failed:
                # Assign failure reason based on weights
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
                    attempt_number=1,
                    created_at=created_time + timedelta(seconds=random.randint(5, 30)),
                )
                failures.append(failure)

        return transactions, failures

    @classmethod
    def populate_database(
        cls,
        db: Session,
        customer_count: int = 150,
        transaction_count: int = 500,
        failure_rate: float = 0.25,
    ) -> dict:
        cust_repo = CustomerRepository(db)
        txn_repo = TransactionRepository(db)

        # Clear existing data if regenerating
        logger.info("Generating synthetic cohorts...")
        customers = cls.generate_customers(customer_count)
        cust_repo.bulk_create(customers)

        transactions, failures = cls.generate_transactions(
            customers, total_count=transaction_count, failure_rate=failure_rate
        )
        txn_repo.bulk_create(transactions)
        txn_repo.bulk_create_failures(failures)

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

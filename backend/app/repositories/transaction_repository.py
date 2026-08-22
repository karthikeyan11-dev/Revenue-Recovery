from sqlalchemy.orm import Session

from app.models.payment_failure import PaymentFailure
from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaction_id: str) -> Transaction | None:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Transaction]:
        return self.db.query(Transaction).offset(offset).limit(limit).all()

    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def bulk_create(self, transactions: list[Transaction]) -> list[Transaction]:
        self.db.add_all(transactions)
        self.db.commit()
        return transactions

    def create_failure(self, failure: PaymentFailure) -> PaymentFailure:
        self.db.add(failure)
        self.db.commit()
        self.db.refresh(failure)
        return failure

    def bulk_create_failures(self, failures: list[PaymentFailure]) -> list[PaymentFailure]:
        self.db.add_all(failures)
        self.db.commit()
        return failures

    def get_unprocessed_failures(self, limit: int | None = None) -> list[PaymentFailure]:
        query = self.db.query(PaymentFailure).filter(~PaymentFailure.revenue_leaks.any())
        if limit:
            query = query.limit(limit)
        return query.all()

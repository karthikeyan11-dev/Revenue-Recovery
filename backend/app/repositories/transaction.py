from sqlalchemy.orm import Session

from app.models.payment_failure import PaymentFailure
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(Transaction, db)

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

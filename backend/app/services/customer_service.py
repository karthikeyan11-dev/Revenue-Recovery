from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)

    def get_customer(self, customer_id: str) -> Customer | None:
        return self.repo.get_by_id(customer_id)

    def list_customers(self, limit: int = 100, offset: int = 0) -> list[Customer]:
        return self.repo.get_all(limit=limit, offset=offset)

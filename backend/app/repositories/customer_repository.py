from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Customer]:
        return self.db.query(Customer).offset(offset).limit(limit).all()

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def bulk_create(self, customers: list[Customer]) -> list[Customer]:
        self.db.add_all(customers)
        self.db.commit()
        return customers

    def count(self) -> int:
        return self.db.query(Customer).count()

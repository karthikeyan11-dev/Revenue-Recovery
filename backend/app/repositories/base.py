from typing import Generic, Type, TypeVar
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic CRUD base repository."""

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> T | None:
        return self.db.query(self.model).filter(getattr(self.model, "id") == id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        return self.db.query(self.model).offset(offset).limit(limit).all()

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def bulk_create(self, entities: list[T]) -> list[T]:
        self.db.add_all(entities)
        self.db.commit()
        return entities

    def count(self) -> int:
        return self.db.query(self.model).count()

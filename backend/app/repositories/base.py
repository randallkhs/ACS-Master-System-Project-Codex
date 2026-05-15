from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base


class BaseRepository[ModelT: Base]:
    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity_id: UUID) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        statement = select(self.model).offset(offset).limit(limit)
        return self.session.scalars(statement).all()

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)

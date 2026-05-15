from uuid import UUID

from sqlalchemy import select

from app.models.visit import Visit
from app.repositories.base import BaseRepository


class VisitRepository(BaseRepository[Visit]):
    model = Visit

    def get_by_work_order_id(self, work_order_id: UUID) -> Visit | None:
        statement = select(self.model).where(self.model.work_order_id == work_order_id)
        return self.session.scalars(statement).first()

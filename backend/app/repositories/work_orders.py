from uuid import UUID

from sqlalchemy import select

from app.models.work_order import WorkOrder
from app.repositories.base import BaseRepository


class WorkOrderRepository(BaseRepository[WorkOrder]):
    model = WorkOrder

    def get_by_job_id(self, job_id: UUID) -> WorkOrder | None:
        statement = select(self.model).where(self.model.job_id == job_id)
        return self.session.scalars(statement).first()

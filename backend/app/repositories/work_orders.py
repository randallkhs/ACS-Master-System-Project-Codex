from app.models.work_order import WorkOrder
from app.repositories.base import BaseRepository


class WorkOrderRepository(BaseRepository[WorkOrder]):
    model = WorkOrder

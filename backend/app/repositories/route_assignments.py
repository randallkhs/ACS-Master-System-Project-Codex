from uuid import UUID

from sqlalchemy import select

from app.models.route_assignment import RouteAssignment
from app.repositories.base import BaseRepository


class RouteAssignmentRepository(BaseRepository[RouteAssignment]):
    model = RouteAssignment

    def get_by_visit_id(self, visit_id: UUID) -> RouteAssignment | None:
        statement = select(self.model).where(self.model.visit_id == visit_id)
        return self.session.scalars(statement).first()

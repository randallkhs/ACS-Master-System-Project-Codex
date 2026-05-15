from app.models.route_assignment import RouteAssignment
from app.repositories.base import BaseRepository


class RouteAssignmentRepository(BaseRepository[RouteAssignment]):
    model = RouteAssignment

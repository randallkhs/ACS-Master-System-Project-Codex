from app.models.visit import Visit
from app.repositories.base import BaseRepository


class VisitRepository(BaseRepository[Visit]):
    model = Visit

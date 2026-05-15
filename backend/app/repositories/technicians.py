from app.models.technician import Technician
from app.repositories.base import BaseRepository


class TechnicianRepository(BaseRepository[Technician]):
    model = Technician

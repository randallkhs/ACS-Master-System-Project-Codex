from app.models.property import Property
from app.repositories.base import BaseRepository


class PropertyRepository(BaseRepository[Property]):
    model = Property

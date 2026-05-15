from app.models.water_emergency import WaterEmergency
from app.repositories.base import BaseRepository


class WaterEmergencyRepository(BaseRepository[WaterEmergency]):
    model = WaterEmergency

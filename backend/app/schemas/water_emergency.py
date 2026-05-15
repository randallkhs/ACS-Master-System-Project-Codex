from pydantic import BaseModel


class WaterEmergencyPlaceholder(BaseModel):
    status: str = "NEW"
    equipment_onsite: bool = False

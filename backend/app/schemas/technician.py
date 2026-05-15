from pydantic import BaseModel


class TechnicianPlaceholder(BaseModel):
    full_name: str
    is_active: bool = True

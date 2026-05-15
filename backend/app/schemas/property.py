from pydantic import BaseModel


class PropertyPlaceholder(BaseModel):
    street_address: str | None = None
    state: str | None = None

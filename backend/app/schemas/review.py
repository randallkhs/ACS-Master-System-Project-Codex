from pydantic import BaseModel


class ReviewItemPlaceholder(BaseModel):
    reason_code: str
    status: str = "OPEN"

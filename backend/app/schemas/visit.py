from pydantic import BaseModel


class VisitPlaceholder(BaseModel):
    visit_type: str | None = None
    status: str = "SCHEDULED"

from datetime import date

from pydantic import BaseModel


class RouteAssignmentPlaceholder(BaseModel):
    route_date: date
    status: str = "PLANNED"

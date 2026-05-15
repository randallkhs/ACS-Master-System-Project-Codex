from pydantic import BaseModel


class WorkOrderPlaceholder(BaseModel):
    status: str = "NEW"
    dispatch_status: str | None = None

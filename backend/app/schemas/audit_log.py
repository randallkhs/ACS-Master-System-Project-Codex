from pydantic import BaseModel


class AuditLogPlaceholder(BaseModel):
    action: str
    entity_type: str | None = None

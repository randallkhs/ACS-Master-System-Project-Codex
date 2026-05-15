from pydantic import BaseModel


class JobPlaceholder(BaseModel):
    job_type: str | None = None
    status: str = "NEW"

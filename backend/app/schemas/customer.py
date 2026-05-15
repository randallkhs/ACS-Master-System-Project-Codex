from pydantic import BaseModel


class CustomerPlaceholder(BaseModel):
    display_name: str

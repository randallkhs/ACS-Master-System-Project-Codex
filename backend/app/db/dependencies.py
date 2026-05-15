from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session

DBSession = Annotated[Session, Depends(get_db_session)]

__all__ = ["DBSession"]

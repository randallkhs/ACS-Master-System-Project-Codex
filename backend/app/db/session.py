from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings

SessionFactory = Callable[[], Session]


def create_database_engine(settings: Settings | None = None) -> Engine:
    resolved_settings = settings or get_settings()
    return create_engine(
        resolved_settings.database_url,
        echo=resolved_settings.database_echo,
        pool_pre_ping=resolved_settings.database_pool_pre_ping,
    )


engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session]:
    db_session = SessionLocal()
    try:
        yield db_session
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()


@contextmanager
def session_scope(session_factory: SessionFactory = SessionLocal) -> Iterator[Session]:
    db_session = session_factory()
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()


def get_db() -> Generator[Session]:
    yield from get_db_session()

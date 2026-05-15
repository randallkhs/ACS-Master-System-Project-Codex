import pytest

from app.db import session as session_module
from app.db.session import get_db_session, session_scope


class SessionStub:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class SessionFactoryStub:
    def __init__(self) -> None:
        self.session = SessionStub()

    def __call__(self) -> SessionStub:
        return self.session


def test_get_db_session_closes_session_after_success(monkeypatch: pytest.MonkeyPatch) -> None:
    session_factory = SessionFactoryStub()
    monkeypatch.setattr(session_module, "SessionLocal", session_factory)
    dependency = get_db_session()

    session = next(dependency)

    assert session is session_factory.session
    with pytest.raises(StopIteration):
        next(dependency)
    assert session_factory.session.closed
    assert not session_factory.session.committed
    assert not session_factory.session.rolled_back


def test_get_db_session_rolls_back_and_closes_after_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_factory = SessionFactoryStub()
    monkeypatch.setattr(session_module, "SessionLocal", session_factory)
    dependency = get_db_session()

    session = next(dependency)

    assert session is session_factory.session
    with pytest.raises(RuntimeError):
        dependency.throw(RuntimeError("request failed"))
    assert session_factory.session.rolled_back
    assert session_factory.session.closed
    assert not session_factory.session.committed


def test_session_scope_commits_and_closes_on_success() -> None:
    session_factory = SessionFactoryStub()

    with session_scope(session_factory) as session:
        assert session is session_factory.session

    assert session_factory.session.committed
    assert session_factory.session.closed
    assert not session_factory.session.rolled_back


def test_session_scope_rolls_back_and_closes_on_exception() -> None:
    session_factory = SessionFactoryStub()

    with pytest.raises(RuntimeError):
        with session_scope(session_factory):
            raise RuntimeError("transaction failed")

    assert session_factory.session.rolled_back
    assert session_factory.session.closed
    assert not session_factory.session.committed

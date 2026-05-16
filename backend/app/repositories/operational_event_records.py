from uuid import UUID

from sqlalchemy import select

from app.models.operational_event_record import OperationalEventRecord
from app.repositories.base import BaseRepository


class OperationalEventRecordRepository(BaseRepository[OperationalEventRecord]):
    model = OperationalEventRecord

    def append(self, record: OperationalEventRecord) -> OperationalEventRecord:
        return self.add(record)

    def delete(self, instance: OperationalEventRecord) -> None:
        msg = (
            "Operational event history is append-only and cannot be deleted through "
            "repository APIs."
        )
        raise TypeError(msg)

    def get_by_event_fingerprint(
        self,
        event_fingerprint: str,
    ) -> OperationalEventRecord | None:
        statement = select(self.model).where(self.model.event_fingerprint == event_fingerprint)
        return self.session.scalars(statement).first()

    def list_for_route_assignment(
        self,
        route_assignment_id: UUID,
    ) -> list[OperationalEventRecord]:
        statement = (
            select(self.model)
            .where(self.model.route_assignment_id == route_assignment_id)
            .order_by(self.model.occurred_at, self.model.recorded_at)
        )
        return list(self.session.scalars(statement).all())

    def list_for_visit(self, visit_id: UUID) -> list[OperationalEventRecord]:
        statement = (
            select(self.model)
            .where(self.model.visit_id == visit_id)
            .order_by(self.model.occurred_at, self.model.recorded_at)
        )
        return list(self.session.scalars(statement).all())

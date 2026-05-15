from uuid import UUID

from sqlalchemy import select

from app.models.job_creation_record import JobCreationRecord
from app.repositories.base import BaseRepository


class JobCreationRecordRepository(BaseRepository[JobCreationRecord]):
    model = JobCreationRecord

    def get_by_intake_processing_record_id(
        self,
        intake_processing_record_id: UUID,
    ) -> JobCreationRecord | None:
        statement = select(self.model).where(
            self.model.intake_processing_record_id == intake_processing_record_id,
        )
        return self.session.scalars(statement).first()

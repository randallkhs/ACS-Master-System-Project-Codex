from app.models.intake_processing_record import IntakeProcessingRecord
from app.repositories.base import BaseRepository


class IntakeProcessingRecordRepository(BaseRepository[IntakeProcessingRecord]):
    model = IntakeProcessingRecord

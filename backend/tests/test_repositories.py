from uuid import uuid4

from app.models import (
    AuditLog,
    Customer,
    IntakeProcessingRecord,
    Job,
    JobCreationRecord,
    Property,
    ReviewItem,
    RouteAssignment,
    Technician,
    Visit,
    WaterEmergency,
    WorkOrder,
)
from app.repositories import (
    AuditLogRepository,
    BaseRepository,
    CustomerRepository,
    IntakeProcessingRecordRepository,
    JobCreationRecordRepository,
    JobRepository,
    PropertyRepository,
    ReviewItemRepository,
    RouteAssignmentRepository,
    TechnicianRepository,
    VisitRepository,
    WaterEmergencyRepository,
    WorkOrderRepository,
)


class ScalarResultStub:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def all(self) -> list[object]:
        return self.rows


class SessionStub:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.deleted: list[object] = []
        self.get_calls: list[tuple[type[object], object]] = []
        self.scalars_called = False
        self.scalar_rows: list[object] = []

    def add(self, instance: object) -> None:
        self.added.append(instance)

    def delete(self, instance: object) -> None:
        self.deleted.append(instance)

    def get(self, model: type[object], entity_id: object) -> object | None:
        self.get_calls.append((model, entity_id))
        return self.scalar_rows[0] if self.scalar_rows else None

    def scalars(self, statement: object) -> ScalarResultStub:
        self.scalars_called = True
        return ScalarResultStub(self.scalar_rows)


def test_domain_repositories_bind_expected_models() -> None:
    session = SessionStub()
    expected_models = [
        (AuditLogRepository, AuditLog),
        (CustomerRepository, Customer),
        (IntakeProcessingRecordRepository, IntakeProcessingRecord),
        (JobRepository, Job),
        (JobCreationRecordRepository, JobCreationRecord),
        (PropertyRepository, Property),
        (ReviewItemRepository, ReviewItem),
        (RouteAssignmentRepository, RouteAssignment),
        (TechnicianRepository, Technician),
        (VisitRepository, Visit),
        (WaterEmergencyRepository, WaterEmergency),
        (WorkOrderRepository, WorkOrder),
    ]

    for repository_class, model_class in expected_models:
        repository = repository_class(session)

        assert isinstance(repository, BaseRepository)
        assert repository.session is session
        assert repository.model is model_class


def test_base_repository_delegates_crud_safe_operations_to_session() -> None:
    class CustomerTestRepository(BaseRepository[Customer]):
        model = Customer

    session = SessionStub()
    repository = CustomerTestRepository(session)
    customer = Customer(display_name="ACS Test Customer")
    customer_id = uuid4()
    session.scalar_rows = [customer]

    assert repository.add(customer) is customer
    assert session.added == [customer]

    assert repository.get(customer_id) is customer
    assert session.get_calls == [(Customer, customer_id)]

    assert repository.list(limit=10, offset=0) == [customer]
    assert session.scalars_called

    repository.delete(customer)
    assert session.deleted == [customer]

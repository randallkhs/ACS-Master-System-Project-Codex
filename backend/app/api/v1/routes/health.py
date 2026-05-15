from fastapi import APIRouter, Request

from app.core.lifecycle import HealthState

router = APIRouter()


@router.get("/health")
def read_health(request: Request) -> dict[str, str | bool | None]:
    settings = request.app.state.settings
    health = getattr(request.app.state, "health", HealthState())
    return health.as_payload(settings)

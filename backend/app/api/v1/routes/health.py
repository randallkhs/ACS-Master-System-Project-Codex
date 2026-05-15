from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def read_health(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    return {
        "status": "ok",
        "service": settings.service_name,
        "environment": settings.environment,
    }

from fastapi import APIRouter

from app.auth.status import build_phase0_auth_status
from app.schemas.auth import AuthStatusResponse

router = APIRouter()


@router.get("/status", response_model=AuthStatusResponse)
def read_auth_status() -> AuthStatusResponse:
    return AuthStatusResponse.model_validate(build_phase0_auth_status())

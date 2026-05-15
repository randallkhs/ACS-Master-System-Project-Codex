from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_jobs_placeholder() -> dict[str, str]:
    return {"status": "placeholder", "module": "jobs"}

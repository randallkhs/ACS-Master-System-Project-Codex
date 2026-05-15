from fastapi import APIRouter

router = APIRouter()


@router.get("")
def read_dispatch_placeholder() -> dict[str, str]:
    return {"status": "placeholder", "module": "dispatch"}

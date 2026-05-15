from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_technicians_placeholder() -> dict[str, str]:
    return {"status": "placeholder", "module": "technicians"}

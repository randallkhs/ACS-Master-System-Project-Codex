from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_review_items_placeholder() -> dict[str, str]:
    return {"status": "placeholder", "module": "manual_review"}

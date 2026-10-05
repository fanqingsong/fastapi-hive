from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", name="manual mount")
def ping():
    return {"mounted": "startup"}

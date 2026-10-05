from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", name="parked")
def ping():
    return {"mounted": "parked"}

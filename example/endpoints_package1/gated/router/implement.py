from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", name="gated")
def ping():
    return {"mounted": "gated"}
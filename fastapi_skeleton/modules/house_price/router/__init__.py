

from fastapi import APIRouter

from fastapi_skeleton.modules.house_price.router.implement import router

api_router = APIRouter()

api_router.include_router(router)



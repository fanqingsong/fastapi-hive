

from fastapi import APIRouter

from demo.xxx_endpoint.house_price.router.implement import router

'''
If you need nested router, use the blow code
'''
# router = APIRouter()
# router.include_router(router, tags=["xxx"], prefix="/xxx")

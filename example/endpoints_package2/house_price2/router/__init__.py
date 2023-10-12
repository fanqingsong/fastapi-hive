

from fastapi import APIRouter

from example.endpoints_package2.house_price2.router.implement import router

'''
If you need nested router, use the blow code
'''
# router = APIRouter()
# router.include_router(router, tags=["xxx"], prefix="/xxx")

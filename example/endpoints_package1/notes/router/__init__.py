

from fastapi import APIRouter

from example.endpoints_package1.notes.router.implement import router

'''
If you need nested router, use the blow code
'''
# router = APIRouter()
# router.include_router(router, tags=["xxx"], prefix="/xxx")

from fastapi import APIRouter

from . import v1


router = APIRouter()
router.include_router(router=v1.router, prefix='/v1')

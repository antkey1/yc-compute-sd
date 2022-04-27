from fastapi import APIRouter

from . import discover

router = APIRouter()
router.include_router(
    router=discover.router, prefix='/discover', tags=['discover']
)

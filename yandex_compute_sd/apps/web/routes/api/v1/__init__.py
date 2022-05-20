from fastapi import APIRouter

from . import discover
from . import kubernetes

router = APIRouter()
router.include_router(
    router=discover.router,
    prefix='/discover',
    tags=['discover'],
)
router.include_router(
    router=kubernetes.router,
    prefix='/kubernetes',
    tags=['kubernetes'],
)

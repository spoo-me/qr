"""
API v1 router composition.

All API endpoints are mounted under /api/v1.
"""

from fastapi import APIRouter

from routes.api_v1.classic import router as classic_router
from routes.api_v1.gradient import router as gradient_router
from routes.api_v1.batch import router as batch_router

router = APIRouter(prefix="/api/v1")
router.include_router(classic_router)
router.include_router(gradient_router)
router.include_router(batch_router)

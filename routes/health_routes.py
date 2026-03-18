"""
Health check endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter

from schemas.dto.responses.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, include_in_schema=False)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")

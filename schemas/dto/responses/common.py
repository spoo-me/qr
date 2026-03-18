"""
Common response DTOs shared across endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Standard error JSON body produced by the AppError exception handler."""

    model_config = ConfigDict(populate_by_name=True)

    error: str
    code: str
    field: Optional[str] = None
    details: Optional[Any] = None


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    model_config = ConfigDict(populate_by_name=True)

    status: str

"""
Request DTOs for QR code generation endpoints.

Validation is handled at the schema level via Pydantic validators.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ClassicQRRequest(BaseModel):
    """Request body/query for the classic (solid-fill) QR code endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    text: str
    fill: str = "black"
    back: str = "white"
    size: Optional[int] = None

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v > 1000:
                raise ValueError("Size is too large")
            if v < 10:
                raise ValueError("Size is too small")
        return v


class GradientQRRequest(BaseModel):
    """Request body/query for the gradient QR code endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    text: str
    gradient1: str = "(106,26,76)"
    gradient2: str = "(64,53,60)"
    back: str = "(255, 255, 255)"
    size: Optional[int] = None

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v > 1000:
                raise ValueError("Size is too large")
            if v < 10:
                raise ValueError("Size is too small")
        return v

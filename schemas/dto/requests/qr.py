"""
Request DTOs for QR code generation endpoints.

Validation is handled at the schema level via Pydantic validators.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from schemas.enums import DataFormat


class ClassicQRRequest(BaseModel):
    """Request body/query for the classic (solid-fill) QR code endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    text: Optional[str] = None
    fill: str = "black"
    back: str = "white"
    size: Optional[int] = None
    format: Optional[DataFormat] = None
    formattings: Optional[str] = None

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v > 1000:
                raise ValueError("Size is too large")
            if v < 10:
                raise ValueError("Size is too small")
        return v

    @model_validator(mode="after")
    def validate_text_or_format(self) -> "ClassicQRRequest":
        if not self.text and not self.format:
            raise ValueError("Text parameter is missing")
        if self.format and not self.formattings:
            raise ValueError("Formattings parameter is missing")
        return self


class GradientQRRequest(BaseModel):
    """Request body/query for the gradient QR code endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    text: Optional[str] = None
    gradient1: str = "(106,26,76)"
    gradient2: str = "(64,53,60)"
    back: str = "(255, 255, 255)"
    size: Optional[int] = None
    format: Optional[DataFormat] = None
    formattings: Optional[str] = None

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v > 1000:
                raise ValueError("Size is too large")
            if v < 10:
                raise ValueError("Size is too small")
        return v

    @model_validator(mode="after")
    def validate_text_or_format(self) -> "GradientQRRequest":
        if not self.text and not self.format:
            raise ValueError("Text parameter is missing")
        if self.format and not self.formattings:
            raise ValueError("Formattings parameter is missing")
        return self

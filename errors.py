"""
Application error hierarchy.

AppError is the base for all typed errors.
"""

from __future__ import annotations

from typing import Any, Optional


class AppError(Exception):
    """Base application error. All typed errors inherit from this."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.field = field
        self.details = details

    def to_dict(self) -> dict:
        payload: dict = {"error": self.message, "code": self.error_code}
        if self.field is not None:
            payload["field"] = self.field
        if self.details is not None:
            payload["details"] = self.details
        return payload


class ValidationError(AppError):
    status_code = 400
    error_code = "validation_error"


class QRGenerationError(AppError):
    status_code = 500
    error_code = "qr_generation_error"

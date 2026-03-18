"""
Global exception handlers.

All API responses get JSON error bodies.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from errors import AppError
from shared.logging import get_logger

log = get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        if not errors:
            return JSONResponse(
                status_code=400,
                content={"error": "Validation error", "code": "validation_error"},
            )

        details = []
        for err in errors:
            # Build field path like "query -> content" or "body -> items -> 0 -> content"
            loc = err.get("loc", ())
            field = " -> ".join(str(part) for part in loc)
            msg = err.get("msg", "Invalid value")
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, ") :]
            details.append({"field": field, "message": msg})

        # Use first error as the top-level message
        first = details[0]
        return JSONResponse(
            status_code=400,
            content={
                "error": first["message"],
                "code": "validation_error",
                "field": first["field"],
                "details": details if len(details) > 1 else None,
            },
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_error_handler(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        details = []
        for err in errors:
            loc = err.get("loc", ())
            field = " -> ".join(str(part) for part in loc)
            msg = err.get("msg", "Invalid value")
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, ") :]
            details.append({"field": field, "message": msg})

        first = (
            details[0] if details else {"field": None, "message": "Validation error"}
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": first["message"],
                "code": "validation_error",
                "field": first["field"],
                "details": details if len(details) > 1 else None,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        log.error(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "An internal server error occurred.",
                "code": "internal_error",
            },
        )

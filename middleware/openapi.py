"""
OpenAPI schema configuration — tags, metadata, and response declarations.

Called once during app creation to configure the Swagger UI at /api-docs.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from schemas.dto.responses.common import ErrorResponse


# ── Shared response declarations for route decorators ─────────────────────────

ERROR_RESPONSES = {
    400: {"description": "Bad Request — invalid parameters", "model": ErrorResponse},
    429: {"description": "Rate limit exceeded", "model": ErrorResponse},
    500: {"description": "Internal server error", "model": ErrorResponse},
}

API_DESCRIPTION = (
    "Open-source QR code generator API with support for classic solid-fill, "
    "gradient, and custom-styled QR codes.\n\n"
    "**Features:**\n"
    "- Classic QR codes with customizable fill and background colors\n"
    "- Gradient QR codes with vertical gradient coloring\n"
    "- Multiple module drawer styles (rounded, circle, bars, gapped)\n"
    "- Multiple gradient types (vertical, horizontal, radial, square)\n"
    "- SVG and PNG output formats\n"
    "- Logo/image embedding in QR codes\n"
    "- Batch QR code generation\n"
    "**Base URL:** `https://qr.spoo.me`"
)

API_CONTACT = {
    "name": "spoo.me",
    "url": "https://spoo.me/contact",
    "email": "support@spoo.me",
}

API_LICENSE = {
    "name": "Apache 2.0",
    "url": "https://github.com/spoo-me/qr/blob/main/LICENSE",
}

OPENAPI_TAGS = [
    {
        "name": "QR Code Generation",
        "description": "Generate styled QR codes in PNG and SVG formats",
    },
    {
        "name": "Batch",
        "description": "Generate multiple QR codes in a single request",
    },
]


def configure_openapi(app: FastAPI, app_url: str = "https://qr.spoo.me") -> None:
    """Attach a custom OpenAPI schema generator with servers and metadata."""

    def _custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
            contact=app.contact,
            license_info=app.license_info,
        )
        openapi_schema["servers"] = [
            {"url": app_url, "description": "Production"},
        ]
        app.openapi_schema = openapi_schema
        return openapi_schema

    app.openapi = _custom_openapi

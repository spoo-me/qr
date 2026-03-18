"""
FastAPI application factory.

create_app() is the single entry point for building the app.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from config import AppSettings
from middleware.error_handler import register_error_handlers
from middleware.logging import RequestLoggingMiddleware
from middleware.openapi import (
    API_CONTACT,
    API_DESCRIPTION,
    API_LICENSE,
    OPENAPI_TAGS,
    configure_openapi,
)
from routes.api_v1 import router as api_v1_router
from routes.health_routes import router as health_router
from routes.page_routes import router as page_router

_SCALAR_CDN = "https://cdn.jsdelivr.net/npm/@scalar/api-reference"
_DOCS_URL = "https://spoo.me/docs/qr/introduction"


def create_app(settings: Optional[AppSettings] = None) -> FastAPI:
    """Create and return a fully configured FastAPI application."""
    if settings is None:
        settings = AppSettings()

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=API_DESCRIPTION,
        contact=API_CONTACT,
        license_info=API_LICENSE,
        # Disable built-in Swagger/ReDoc — we use Scalar
        docs_url=None,
        redoc_url=None,
        openapi_tags=OPENAPI_TAGS,
    )

    # Store settings on app state for access in dependencies
    app.state.settings = settings

    configure_openapi(app, app_url=settings.app_url)

    # ── /docs — Scalar in dev, redirect in prod ──────────────────────────
    _is_prod = settings.is_production
    _app_name = settings.app_name

    @app.get("/docs", include_in_schema=False)
    async def docs():
        if _is_prod:
            return RedirectResponse(_DOCS_URL)
        return HTMLResponse(
            f"""<!doctype html>
<html>
<head>
    <title>{_app_name} — API Docs</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body>
    <script id="api-reference" data-url="/openapi.json"></script>
    <script src="{_SCALAR_CDN}"></script>
</body>
</html>"""
        )

    # ── Middleware (registered in reverse execution order) ─────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    # ── Error handlers ────────────────────────────────────────────────────
    register_error_handlers(app)

    # ── Static files ──────────────────────────────────────────────────────
    _static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(_static_dir):
        app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    # ── Routers ───────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(api_v1_router)
    app.include_router(page_router)

    return app

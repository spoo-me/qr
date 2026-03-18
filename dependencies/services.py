"""
Service dependency providers.

Thin wrappers that construct service instances for route-layer injection.
"""

from __future__ import annotations

from services.qr_service import QRService


def get_qr_service() -> QRService:
    """Return a QRService instance."""
    return QRService()

"""
Shared fixtures for all integration tests.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import create_app


@pytest.fixture
def client():
    """Create a test client for the full application."""
    app = create_app()
    with TestClient(app) as c:
        yield c

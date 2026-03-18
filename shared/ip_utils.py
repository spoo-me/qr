"""
IP address utilities.
"""

from __future__ import annotations

from typing import Optional

from starlette.requests import Request

# Header priority for client IP resolution
_IP_HEADERS = [
    "CF-Connecting-IP",
    "X-Real-IP",
    "X-Forwarded-For",
]


def get_client_ip(request: Request) -> Optional[str]:
    """Extract the client IP from proxy headers or the direct connection."""
    for header in _IP_HEADERS:
        value = request.headers.get(header)
        if value:
            # X-Forwarded-For may contain multiple IPs — take the first
            return value.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None

"""
Gradient QR code generation endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from dependencies.services import get_qr_service
from middleware.openapi import ERROR_RESPONSES
from schemas.enums import GradientDirection, ModuleStyle, OutputFormat
from services.qr_service import QRService

router = APIRouter(tags=["QR Code Generation"])

_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"
}


@router.get(
    "/gradient",
    response_class=StreamingResponse,
    responses=ERROR_RESPONSES,
    summary="Gradient QR",
    description="Generate a QR code with gradient coloring. PNG output only.",
)
async def generate_gradient_get(
    content: str = Query(..., description="Text or URL to encode"),
    start: str = Query(
        "#6a1a4c", description="Gradient start color (hex, name, or RGB)"
    ),
    end: str = Query("#40353c", description="Gradient end color (hex, name, or RGB)"),
    background: str = Query("#ffffff", description="Background color"),
    size: Optional[int] = Query(
        None, ge=10, le=1000, description="Output size in pixels"
    ),
    style: ModuleStyle = Query(ModuleStyle.SQUARE, description="Module drawing style"),
    direction: GradientDirection = Query(
        GradientDirection.VERTICAL, description="Gradient direction"
    ),
    output: OutputFormat = Query(
        OutputFormat.PNG, description="Output format (PNG only for gradient)"
    ),
    qr_service: QRService = Depends(get_qr_service),
) -> StreamingResponse:
    stream, media_type = await qr_service.generate_gradient(
        content=content,
        start=start,
        end=end,
        background=background,
        size=size,
        style=style,
        direction=direction,
        output=output,
    )
    return StreamingResponse(stream, media_type=media_type, headers=_CACHE_HEADERS)


@router.post(
    "/gradient",
    response_class=StreamingResponse,
    responses=ERROR_RESPONSES,
    summary="Gradient QR + Logo",
    description=(
        "Same as GET, plus an optional logo image file to embed in the center.\n\n"
        "Send the logo as a **multipart file upload** in the `logo` field:\n\n"
        "```bash\n"
        'curl -X POST "https://qr.spoo.me/api/v1/gradient?content=https://example.com" \\\n'
        '  -F "logo=@my-logo.png"\n'
        "```"
    ),
)
async def generate_gradient_post(
    content: str = Query(..., description="Text or URL to encode"),
    start: str = Query(
        "#6a1a4c", description="Gradient start color (hex, name, or RGB)"
    ),
    end: str = Query("#40353c", description="Gradient end color (hex, name, or RGB)"),
    background: str = Query("#ffffff", description="Background color"),
    size: Optional[int] = Query(
        None, ge=10, le=1000, description="Output size in pixels"
    ),
    style: ModuleStyle = Query(ModuleStyle.SQUARE, description="Module drawing style"),
    direction: GradientDirection = Query(
        GradientDirection.VERTICAL, description="Gradient direction"
    ),
    logo: Optional[UploadFile] = File(
        None, description="Logo image to embed (optional)"
    ),
    qr_service: QRService = Depends(get_qr_service),
) -> StreamingResponse:
    logo_bytes = await logo.read() if logo else None
    stream, media_type = await qr_service.generate_gradient(
        content=content,
        start=start,
        end=end,
        background=background,
        size=size,
        style=style,
        direction=direction,
        output=OutputFormat.PNG,
        logo_image=logo_bytes,
    )
    return StreamingResponse(stream, media_type=media_type)

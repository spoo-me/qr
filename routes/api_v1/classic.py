"""
Classic QR code generation endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from dependencies.services import get_qr_service
from middleware.openapi import ERROR_RESPONSES
from schemas.enums import ModuleStyle, OutputFormat
from services.qr_service import QRService

router = APIRouter(tags=["QR Code Generation"])

_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"
}


@router.get(
    "/classic",
    response_class=StreamingResponse,
    responses=ERROR_RESPONSES,
    summary="Classic QR",
    description="Generate a QR code with solid fill and background colors.",
)
async def generate_classic_get(
    content: str = Query(..., description="Text or URL to encode"),
    color: str = Query("black", description="Fill color (hex, name, or RGB)"),
    background: str = Query("white", description="Background color"),
    size: Optional[int] = Query(
        None, ge=10, le=1000, description="Output size in pixels"
    ),
    style: ModuleStyle = Query(ModuleStyle.ROUNDED, description="Module drawing style"),
    output: OutputFormat = Query(OutputFormat.PNG, description="Output format"),
    qr_service: QRService = Depends(get_qr_service),
) -> StreamingResponse:
    stream, media_type = await qr_service.generate_classic(
        content=content,
        color=color,
        background=background,
        size=size,
        style=style,
        output=output,
    )
    return StreamingResponse(stream, media_type=media_type, headers=_CACHE_HEADERS)


@router.post(
    "/classic",
    response_class=StreamingResponse,
    responses=ERROR_RESPONSES,
    summary="Classic QR + Logo",
    description=(
        "Same as GET, plus an optional logo image file to embed in the center.\n\n"
        "Send the logo as a **multipart file upload** in the `logo` field:\n\n"
        "```bash\n"
        'curl -X POST "https://qr.spoo.me/api/v1/classic?content=https://example.com" \\\n'
        '  -F "logo=@my-logo.png"\n'
        "```"
    ),
)
async def generate_classic_post(
    content: str = Query(..., description="Text or URL to encode"),
    color: str = Query("black", description="Fill color (hex, name, or RGB)"),
    background: str = Query("white", description="Background color"),
    size: Optional[int] = Query(
        None, ge=10, le=1000, description="Output size in pixels"
    ),
    style: ModuleStyle = Query(ModuleStyle.ROUNDED, description="Module drawing style"),
    output: OutputFormat = Query(OutputFormat.PNG, description="Output format"),
    logo: Optional[UploadFile] = File(
        None, description="Logo image to embed (optional)"
    ),
    qr_service: QRService = Depends(get_qr_service),
) -> StreamingResponse:
    logo_bytes = await logo.read() if logo else None
    effective_output = OutputFormat.PNG if logo_bytes else output
    stream, media_type = await qr_service.generate_classic(
        content=content,
        color=color,
        background=background,
        size=size,
        style=style,
        output=effective_output,
        logo_image=logo_bytes,
    )
    return StreamingResponse(stream, media_type=media_type)

"""
Batch QR code generation endpoint.
"""

from __future__ import annotations

import io
import os
import re
import zipfile
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, field_validator

from dependencies.services import get_qr_service
from middleware.openapi import ERROR_RESPONSES
from schemas.enums import ModuleStyle, OutputFormat
from services.qr_service import QRService

router = APIRouter(tags=["Batch"])


class BatchItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    content: str
    color: str = "black"
    background: str = "white"
    size: Optional[int] = None
    style: ModuleStyle = ModuleStyle.ROUNDED
    output: OutputFormat = OutputFormat.PNG
    filename: Optional[str] = None

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v > 1000:
                raise ValueError("Size is too large")
            if v < 10:
                raise ValueError("Size is too small")
        return v


class BatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[BatchItem]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[BatchItem]) -> list[BatchItem]:
        if len(v) == 0:
            raise ValueError("At least one item is required")
        if len(v) > 20:
            raise ValueError("Batch size cannot exceed 20 items")
        return v


@router.post(
    "/batch",
    response_class=StreamingResponse,
    responses=ERROR_RESPONSES,
    summary="Batch QR",
    description="Generate up to 20 QR codes in one request. Returns a ZIP archive.",
)
async def generate_batch(
    body: BatchRequest,
    qr_service: QRService = Depends(get_qr_service),
) -> StreamingResponse:
    results = await qr_service.generate_batch(
        items=[item.model_dump() for item in body.items],
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, (stream, _) in enumerate(results):
            item = body.items[i]
            ext = "svg" if item.output == OutputFormat.SVG else "png"
            raw_name = item.filename or f"qrcode_{i + 1}"
            # Sanitize: strip path components and drive letters to prevent zip slip
            filename = os.path.basename(raw_name)
            filename = re.sub(r"[^\w\-.]", "_", filename) or f"qrcode_{i + 1}"
            if not filename.endswith(f".{ext}"):
                filename = f"{filename}.{ext}"
            zf.writestr(filename, stream.read())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=qrcodes.zip"},
    )

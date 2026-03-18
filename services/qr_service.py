"""
QR code generation service.

Fully async — CPU-bound work is offloaded to a thread pool via asyncio.to_thread().
"""

from __future__ import annotations

import asyncio
import io
import re
import urllib.parse
from typing import Optional

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.svg import SvgPathImage
from qrcode.image.styles.colormasks import (
    HorizontalGradiantColorMask,
    RadialGradiantColorMask,
    SolidFillColorMask,
    SquareGradiantColorMask,
    VerticalGradiantColorMask,
)
from qrcode.image.styles.moduledrawers.pil import (
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
    HorizontalBarsDrawer,
    RoundedModuleDrawer,
    SquareModuleDrawer,
    VerticalBarsDrawer,
)

from errors import QRGenerationError, ValidationError
from schemas.enums import GradientDirection, ModuleStyle, OutputFormat
from shared.color import parse_color
from shared.logging import get_logger

log = get_logger(__name__)

MODULE_DRAWERS = {
    ModuleStyle.ROUNDED: RoundedModuleDrawer,
    ModuleStyle.SQUARE: SquareModuleDrawer,
    ModuleStyle.CIRCLE: CircleModuleDrawer,
    ModuleStyle.GAPPED: GappedSquareModuleDrawer,
    ModuleStyle.HORIZONTAL_BARS: HorizontalBarsDrawer,
    ModuleStyle.VERTICAL_BARS: VerticalBarsDrawer,
}

GRADIENT_MASKS = {
    GradientDirection.VERTICAL: VerticalGradiantColorMask,
    GradientDirection.HORIZONTAL: HorizontalGradiantColorMask,
    GradientDirection.RADIAL: RadialGradiantColorMask,
    GradientDirection.SQUARE: SquareGradiantColorMask,
}


def _to_hex(color_tuple) -> str:
    if color_tuple == "transparent":
        return "#000000"
    return "#{:02x}{:02x}{:02x}".format(*color_tuple)


class QRService:
    """Stateless async service for generating styled QR code images."""

    async def generate_classic(
        self,
        *,
        content: str,
        color: str = "black",
        background: str = "white",
        size: Optional[int] = None,
        style: ModuleStyle = ModuleStyle.ROUNDED,
        output: OutputFormat = OutputFormat.PNG,
        logo_image: Optional[bytes] = None,
    ) -> tuple[io.BytesIO, str]:
        """Generate a classic QR code with solid fill colors."""
        text = self._parse_content(content)

        fill_color = parse_color(urllib.parse.unquote(color))
        back_color = parse_color(urllib.parse.unquote(background))

        if output == OutputFormat.SVG:
            fill_hex = _to_hex(fill_color)
            back_hex = "#ffffff" if back_color == "transparent" else _to_hex(back_color)
            return await asyncio.to_thread(
                self._render_svg, text, size, fill_hex, back_hex
            )

        if fill_color == "transparent":
            fill_color = (0, 0, 0)

        drawer_cls = MODULE_DRAWERS.get(style, RoundedModuleDrawer)
        return await asyncio.to_thread(
            self._generate_classic_sync,
            text,
            fill_color,
            back_color,
            size,
            drawer_cls,
            logo_image,
        )

    async def generate_gradient(
        self,
        *,
        content: str,
        start: str = "#6a1a4c",
        end: str = "#40353c",
        background: str = "#ffffff",
        size: Optional[int] = None,
        style: ModuleStyle = ModuleStyle.SQUARE,
        direction: GradientDirection = GradientDirection.VERTICAL,
        output: OutputFormat = OutputFormat.PNG,
        logo_image: Optional[bytes] = None,
    ) -> tuple[io.BytesIO, str]:
        """Generate a gradient QR code."""
        text = self._parse_content(content)

        if output == OutputFormat.SVG:
            raise ValidationError(
                "SVG output is not supported for gradient QR codes. Use PNG instead.",
                field="output",
            )

        start_color = parse_color(urllib.parse.unquote(start))
        end_color = parse_color(urllib.parse.unquote(end))
        back_color = parse_color(urllib.parse.unquote(background))

        drawer_cls = MODULE_DRAWERS.get(style, SquareModuleDrawer)
        mask_cls = GRADIENT_MASKS.get(direction, VerticalGradiantColorMask)
        return await asyncio.to_thread(
            self._generate_gradient_sync,
            text,
            start_color,
            end_color,
            back_color,
            size,
            drawer_cls,
            mask_cls,
            logo_image,
        )

    async def generate_batch(
        self, *, items: list[dict]
    ) -> list[tuple[io.BytesIO, str]]:
        """Generate multiple QR codes concurrently."""
        if len(items) > 20:
            raise ValidationError("Batch size cannot exceed 20 items", field="items")

        tasks = [
            self.generate_classic(
                content=item.get("content", ""),
                color=item.get("color", "black"),
                background=item.get("background", "white"),
                size=item.get("size"),
                style=ModuleStyle(item.get("style", "rounded")),
                output=OutputFormat(item.get("output", "png")),
            )
            for item in items
        ]

        try:
            return await asyncio.gather(*tasks)
        except (ValidationError, QRGenerationError):
            raise
        except Exception as e:
            raise ValidationError(f"Batch generation failed: {e}", field="items")

    # ── Sync helpers (run in thread pool) ─────────────────────────────────────

    def _generate_classic_sync(
        self, text, fill_color, back_color, size, drawer_cls, logo_image
    ):
        import os

        qr = self._build_qr(text, high_correction=bool(logo_image))
        logo_path = self._save_logo_to_tempfile(logo_image) if logo_image else None
        try:
            kwargs = dict(
                image_factory=StyledPilImage,
                module_drawer=drawer_cls(),
                color_mask=SolidFillColorMask(back_color, fill_color),
            )
            if logo_path:
                kwargs["embedded_image_path"] = logo_path
            qr_image = qr.make_image(**kwargs)
        except Exception as e:
            raise QRGenerationError(f"Error generating QR code: {e}")
        finally:
            if logo_path:
                os.unlink(logo_path)
        return self._render_png(qr_image, size)

    def _generate_gradient_sync(
        self,
        text,
        start_color,
        end_color,
        back_color,
        size,
        drawer_cls,
        mask_cls,
        logo_image,
    ):
        import os

        qr = self._build_qr(text, high_correction=bool(logo_image))
        logo_path = self._save_logo_to_tempfile(logo_image) if logo_image else None
        try:
            kwargs = dict(
                image_factory=StyledPilImage,
                module_drawer=drawer_cls(),
                color_mask=mask_cls(back_color, start_color, end_color),
            )
            if logo_path:
                kwargs["embedded_image_path"] = logo_path
            qr_image = qr.make_image(**kwargs)
        except Exception as e:
            raise QRGenerationError(f"Error generating QR code: {e}")
        finally:
            if logo_path:
                os.unlink(logo_path)
        return self._render_png(qr_image, size)

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_content(content: Optional[str]) -> str:
        if not content:
            raise ValidationError("Content is required", field="content")
        try:
            return urllib.parse.unquote(content).strip()
        except Exception:
            raise ValidationError("Invalid content", field="content")

    @staticmethod
    def _build_qr(data: str, high_correction: bool = False) -> qrcode.QRCode:
        error_level = (
            qrcode.constants.ERROR_CORRECT_H
            if high_correction
            else qrcode.constants.ERROR_CORRECT_L
        )
        qr = qrcode.QRCode(
            version=None, error_correction=error_level, box_size=10, border=4
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr

    @staticmethod
    def _save_logo_to_tempfile(logo_bytes: bytes) -> str:
        import tempfile

        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(logo_bytes)
        tmp.close()
        return tmp.name

    @staticmethod
    def _render_png(qr_image, size: Optional[int]) -> tuple[io.BytesIO, str]:
        if size and hasattr(qr_image, "resize"):
            qr_image = qr_image.resize((size, size), resample=0)
        stream = io.BytesIO()
        qr_image.save(stream, format="PNG")
        stream.seek(0)
        return stream, "image/png"

    def _render_svg(self, data, size, fill_color="#000000", back_color="#ffffff"):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        try:
            svg_image = qr.make_image(image_factory=SvgPathImage)
        except Exception as e:
            raise QRGenerationError(f"Error generating SVG QR code: {e}")

        stream = io.BytesIO()
        svg_image.save(stream)
        svg_str = stream.getvalue().decode("utf-8")
        svg_str = re.sub(r'\s+fill_color="[^"]*"', "", svg_str)
        svg_str = re.sub(r'\s+back_color="[^"]*"', "", svg_str)
        svg_str = re.sub(
            r"(<svg[^>]*>)",
            rf'\1<rect width="100%" height="100%" fill="{back_color}"/>',
            svg_str,
        )
        svg_str = svg_str.replace("<path ", f'<path fill="{fill_color}" ')

        out = io.BytesIO(svg_str.encode("utf-8"))
        out.seek(0)
        return out, "image/svg+xml"

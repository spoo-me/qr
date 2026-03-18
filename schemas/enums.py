"""
Enumerations used across the QR code service.
"""

from enum import Enum


class ModuleStyle(str, Enum):
    """QR code module (pixel) drawing styles."""

    ROUNDED = "rounded"
    SQUARE = "square"
    CIRCLE = "circle"
    GAPPED = "gapped"
    HORIZONTAL_BARS = "horizontal_bars"
    VERTICAL_BARS = "vertical_bars"


class GradientDirection(str, Enum):
    """Gradient direction/shape for gradient QR codes."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    RADIAL = "radial"
    SQUARE = "square"


class OutputFormat(str, Enum):
    """Output image format."""

    PNG = "png"
    SVG = "svg"

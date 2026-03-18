"""
Color parsing utilities.

Supports named colors, hex (#RRGGBB), rgb(r,g,b), and (r,g,b) formats.
"""

from __future__ import annotations

from errors import ValidationError

NAMED_COLORS: dict[str, tuple[int, int, int] | str] = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "gray": (128, 128, 128),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "transparent": "transparent",
}


def parse_color(color_str: str) -> tuple[int, int, int] | str:
    """Parse a color string into an RGB tuple or 'transparent'.

    Raises ValidationError if the color format is invalid.
    """
    try:
        lower = color_str.lower()
        if lower in NAMED_COLORS:
            return NAMED_COLORS[lower]

        if color_str.startswith("#"):
            hex_str = color_str.lstrip("#")
            if len(hex_str) == 6:
                return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))
            raise ValueError("Invalid hex color format")

        if color_str.startswith("rgb(") and color_str.endswith(")"):
            inner = color_str[4:-1]
            values = [int(x.strip()) for x in inner.split(",")]
            if len(values) == 3:
                return tuple(values)
            raise ValueError("Invalid RGB color format")

        if color_str.startswith("(") and color_str.endswith(")"):
            inner = color_str[1:-1]
            values = [int(x.strip()) for x in inner.split(",")]
            if len(values) == 3:
                return tuple(values)
            raise ValueError("Invalid RGB color format")

        # Assume bare hex without # prefix
        if len(color_str) == 6:
            return tuple(int(color_str[i : i + 2], 16) for i in (0, 2, 4))

        raise ValueError("Invalid color format")
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid color format: {color_str}", field="color")

"""Unit tests for services.qr_service."""

import io

import pytest

from errors import ValidationError
from schemas.enums import GradientDirection, ModuleStyle, OutputFormat
from services.qr_service import QRService


@pytest.fixture
def svc():
    return QRService()


class TestGenerateClassic:
    @pytest.mark.anyio
    async def test_basic(self, svc):
        stream, mt = await svc.generate_classic(content="https://example.com")
        assert mt == "image/png"
        assert stream.read()[:4] == b"\x89PNG"

    @pytest.mark.anyio
    async def test_hex_colors(self, svc):
        stream, _ = await svc.generate_classic(
            content="test", color="#FF0000", background="#00FF00"
        )
        assert isinstance(stream, io.BytesIO)

    @pytest.mark.anyio
    async def test_with_size(self, svc):
        stream, _ = await svc.generate_classic(content="test", size=200)
        assert isinstance(stream, io.BytesIO)

    @pytest.mark.anyio
    async def test_transparent_fill(self, svc):
        stream, _ = await svc.generate_classic(content="test", color="transparent")
        assert isinstance(stream, io.BytesIO)

    @pytest.mark.anyio
    async def test_missing_content(self, svc):
        with pytest.raises(ValidationError, match="Content is required"):
            await svc.generate_classic(content="")

    @pytest.mark.anyio
    async def test_invalid_color(self, svc):
        with pytest.raises(ValidationError, match="Invalid color format"):
            await svc.generate_classic(content="test", color="not-a-color")

    @pytest.mark.anyio
    @pytest.mark.parametrize("s", list(ModuleStyle))
    async def test_all_styles(self, svc, s):
        stream, _ = await svc.generate_classic(content="test", style=s)
        assert isinstance(stream, io.BytesIO)

    @pytest.mark.anyio
    async def test_svg_output(self, svc):
        stream, mt = await svc.generate_classic(content="test", output=OutputFormat.SVG)
        assert mt == "image/svg+xml"
        assert b"<svg" in stream.read()

    @pytest.mark.anyio
    async def test_svg_with_colors(self, svc):
        stream, _ = await svc.generate_classic(
            content="test",
            color="#ff0000",
            background="#00ff00",
            output=OutputFormat.SVG,
        )
        svg = stream.read().decode()
        assert 'fill="#ff0000"' in svg
        assert 'fill="#00ff00"' in svg


class TestGenerateGradient:
    @pytest.mark.anyio
    async def test_basic(self, svc):
        stream, mt = await svc.generate_gradient(content="https://example.com")
        assert mt == "image/png"
        assert stream.read()[:4] == b"\x89PNG"

    @pytest.mark.anyio
    async def test_with_size(self, svc):
        stream, _ = await svc.generate_gradient(content="test", size=300)
        assert isinstance(stream, io.BytesIO)

    @pytest.mark.anyio
    @pytest.mark.parametrize("d", list(GradientDirection))
    async def test_all_directions(self, svc, d):
        stream, _ = await svc.generate_gradient(content="test", direction=d)
        assert isinstance(stream, io.BytesIO)

    @pytest.mark.anyio
    async def test_svg_raises(self, svc):
        with pytest.raises(ValidationError, match="SVG output is not supported"):
            await svc.generate_gradient(content="test", output=OutputFormat.SVG)


class TestEmbedLogo:
    def _logo(self) -> bytes:
        from PIL import Image

        img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @pytest.mark.anyio
    async def test_classic_logo(self, svc):
        stream, mt = await svc.generate_classic(
            content="https://example.com", logo_image=self._logo()
        )
        assert mt == "image/png"

    @pytest.mark.anyio
    async def test_gradient_logo(self, svc):
        stream, _ = await svc.generate_gradient(
            content="https://example.com", logo_image=self._logo()
        )
        assert isinstance(stream, io.BytesIO)


class TestBatch:
    @pytest.mark.anyio
    async def test_concurrent(self, svc):
        items = [
            {"content": "https://example.com"},
            {"content": "https://google.com", "color": "#FF0000"},
        ]
        results = await svc.generate_batch(items=items)
        assert len(results) == 2

    @pytest.mark.anyio
    async def test_too_many(self, svc):
        items = [{"content": f"item{i}"} for i in range(21)]
        with pytest.raises(ValidationError, match="Batch size cannot exceed"):
            await svc.generate_batch(items=items)


class TestParseContent:
    def test_basic(self, svc):
        assert svc._parse_content("hello") == "hello"

    def test_url_encoded(self, svc):
        assert svc._parse_content("hello%20world") == "hello world"

    def test_empty_raises(self, svc):
        with pytest.raises(ValidationError, match="Content is required"):
            svc._parse_content("")

    def test_none_raises(self, svc):
        with pytest.raises(ValidationError, match="Content is required"):
            svc._parse_content(None)

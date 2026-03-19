"""Unit tests for QRService internal helpers."""

import pytest

from services.qr_service import QRService, _to_hex


class TestToHex:
    def test_basic_tuple(self):
        assert _to_hex((255, 0, 0)) == "#ff0000"

    def test_black(self):
        assert _to_hex((0, 0, 0)) == "#000000"

    def test_white(self):
        assert _to_hex((255, 255, 255)) == "#ffffff"

    def test_transparent_returns_black(self):
        assert _to_hex("transparent") == "#000000"


class TestBuildQR:
    def test_returns_qr_object(self):
        svc = QRService()
        qr = svc._build_qr("hello")
        assert qr is not None
        assert qr.data_list is not None

    def test_high_correction(self):
        svc = QRService()
        qr = svc._build_qr("hello", high_correction=True)
        import qrcode.constants

        assert qr.error_correction == qrcode.constants.ERROR_CORRECT_H

    def test_low_correction_default(self):
        svc = QRService()
        qr = svc._build_qr("hello", high_correction=False)
        import qrcode.constants

        assert qr.error_correction == qrcode.constants.ERROR_CORRECT_L


class TestSaveLogoToTempfile:
    def test_creates_file(self):
        import os

        svc = QRService()
        # Minimal PNG bytes
        from PIL import Image
        import io

        img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        logo_bytes = buf.getvalue()

        path = svc._save_logo_to_tempfile(logo_bytes)
        try:
            assert os.path.exists(path)
            assert path.endswith(".png")
            with open(path, "rb") as f:
                assert f.read() == logo_bytes
        finally:
            os.unlink(path)


class TestGenerateClassicTransparentColor:
    @pytest.mark.anyio
    async def test_transparent_fill_falls_back_to_black(self):
        """Transparent fill is replaced with (0,0,0) for PIL compatibility."""
        svc = QRService()
        stream, mt = await svc.generate_classic(content="test", color="transparent")
        assert mt == "image/png"

    @pytest.mark.anyio
    async def test_svg_transparent_background_becomes_white(self):
        from schemas.enums import OutputFormat

        svc = QRService()
        stream, mt = await svc.generate_classic(
            content="test",
            color="#ff0000",
            background="transparent",
            output=OutputFormat.SVG,
        )
        assert mt == "image/svg+xml"
        svg = stream.read().decode()
        assert 'fill="#ffffff"' in svg  # transparent bg becomes white in SVG

    @pytest.mark.anyio
    async def test_transparent_background_png_raises(self):
        """PIL can't handle 'transparent' as a background color string."""
        from errors import QRGenerationError

        svc = QRService()
        with pytest.raises(QRGenerationError):
            await svc.generate_classic(content="test", background="transparent")


class TestGenerateBatchEdgeCases:
    @pytest.mark.anyio
    async def test_single_item(self):
        svc = QRService()
        results = await svc.generate_batch(items=[{"content": "hello"}])
        assert len(results) == 1

    @pytest.mark.anyio
    async def test_batch_with_invalid_content(self):
        from errors import ValidationError

        svc = QRService()
        with pytest.raises(ValidationError):
            await svc.generate_batch(items=[{"content": ""}])

    @pytest.mark.anyio
    async def test_max_batch_size(self):
        svc = QRService()
        items = [{"content": f"item{i}"} for i in range(20)]
        results = await svc.generate_batch(items=items)
        assert len(results) == 20

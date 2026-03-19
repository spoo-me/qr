"""Unit tests for schemas.dto.requests.qr — request validation."""

import pytest
from pydantic import ValidationError

from schemas.dto.requests.qr import ClassicQRRequest, GradientQRRequest


class TestClassicQRRequest:
    def test_defaults(self):
        req = ClassicQRRequest(text="hello")
        assert req.text == "hello"
        assert req.fill == "black"
        assert req.back == "white"
        assert req.size is None

    def test_custom_values(self):
        req = ClassicQRRequest(text="url", fill="#ff0000", back="#00ff00", size=200)
        assert req.fill == "#ff0000"
        assert req.size == 200

    def test_size_none_is_valid(self):
        req = ClassicQRRequest(text="test", size=None)
        assert req.size is None

    def test_size_min_boundary(self):
        req = ClassicQRRequest(text="test", size=10)
        assert req.size == 10

    def test_size_max_boundary(self):
        req = ClassicQRRequest(text="test", size=1000)
        assert req.size == 1000

    def test_size_too_large(self):
        with pytest.raises(ValidationError, match="Size is too large"):
            ClassicQRRequest(text="test", size=1001)

    def test_size_too_small(self):
        with pytest.raises(ValidationError, match="Size is too small"):
            ClassicQRRequest(text="test", size=9)


class TestGradientQRRequest:
    def test_defaults(self):
        req = GradientQRRequest(text="hello")
        assert req.gradient1 == "(106,26,76)"
        assert req.gradient2 == "(64,53,60)"
        assert req.back == "(255, 255, 255)"
        assert req.size is None

    def test_custom_values(self):
        req = GradientQRRequest(
            text="url", gradient1="#ff0000", gradient2="#0000ff", size=500
        )
        assert req.gradient1 == "#ff0000"
        assert req.size == 500

    def test_size_too_large(self):
        with pytest.raises(ValidationError, match="Size is too large"):
            GradientQRRequest(text="test", size=1001)

    def test_size_too_small(self):
        with pytest.raises(ValidationError, match="Size is too small"):
            GradientQRRequest(text="test", size=9)

    def test_size_boundaries(self):
        assert GradientQRRequest(text="t", size=10).size == 10
        assert GradientQRRequest(text="t", size=1000).size == 1000

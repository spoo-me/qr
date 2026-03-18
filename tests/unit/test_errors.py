"""Unit tests for errors — error hierarchy."""

from errors import AppError, QRGenerationError, ValidationError


class TestAppError:
    def test_default_status_code(self):
        err = AppError("something broke")
        assert err.status_code == 500
        assert err.error_code == "internal_error"

    def test_to_dict(self):
        err = AppError("msg", field="name", details={"key": "val"})
        d = err.to_dict()
        assert d["error"] == "msg"
        assert d["code"] == "internal_error"
        assert d["field"] == "name"
        assert d["details"] == {"key": "val"}

    def test_to_dict_minimal(self):
        err = AppError("msg")
        d = err.to_dict()
        assert "field" not in d
        assert "details" not in d


class TestValidationError:
    def test_status_code(self):
        err = ValidationError("bad input")
        assert err.status_code == 400
        assert err.error_code == "validation_error"


class TestQRGenerationError:
    def test_status_code(self):
        err = QRGenerationError("failed to generate")
        assert err.status_code == 500
        assert err.error_code == "qr_generation_error"

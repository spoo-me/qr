"""Integration tests for error handler middleware — covers all exception handlers."""


class TestValidationErrors:
    """RequestValidationError handler via invalid query params."""

    def test_missing_required_param(self, client):
        resp = client.get("/api/v1/classic")
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == "validation_error"
        assert "field" in body

    def test_size_out_of_range(self, client):
        resp = client.get("/api/v1/classic", params={"content": "test", "size": 5000})
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == "validation_error"

    def test_invalid_enum_style(self, client):
        resp = client.get(
            "/api/v1/classic", params={"content": "test", "style": "nonexistent"}
        )
        assert resp.status_code == 422 or resp.status_code == 400

    def test_invalid_enum_output(self, client):
        resp = client.get(
            "/api/v1/classic", params={"content": "test", "output": "bmp"}
        )
        assert resp.status_code == 422 or resp.status_code == 400


class TestAppErrors:
    """AppError handler via ValidationError raised by service layer."""

    def test_invalid_color_returns_400(self, client):
        resp = client.get(
            "/api/v1/classic", params={"content": "test", "color": "not-a-color"}
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == "validation_error"
        assert "color" in body.get("error", "").lower()

    def test_empty_content_returns_400(self, client):
        resp = client.get("/api/v1/gradient", params={"content": ""})
        assert resp.status_code == 400

    def test_svg_gradient_returns_400(self, client):
        resp = client.get(
            "/api/v1/gradient", params={"content": "test", "output": "svg"}
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "SVG" in body["error"]


class TestBatchValidationErrors:
    """Pydantic ValidationError handler via batch endpoint."""

    def test_empty_items(self, client):
        resp = client.post("/api/v1/batch", json={"items": []})
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == "validation_error"

    def test_too_many_items(self, client):
        body = {"items": [{"content": f"item{i}"} for i in range(21)]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 400

    def test_batch_item_size_too_large(self, client):
        body = {"items": [{"content": "test", "size": 5000}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 400

    def test_batch_item_size_too_small(self, client):
        body = {"items": [{"content": "test", "size": 1}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 400


class TestLogoSizeLimit:
    """Logo upload size validation."""

    def test_classic_logo_too_large(self, client):
        big_logo = b"\x00" * (2 * 1024 * 1024 + 1)  # Just over 2 MB
        resp = client.post(
            "/api/v1/classic",
            data={"content": "https://example.com"},
            files={"logo": ("big.png", big_logo, "image/png")},
        )
        assert resp.status_code == 400
        assert "2 MB" in resp.json()["error"]

    def test_gradient_logo_too_large(self, client):
        big_logo = b"\x00" * (2 * 1024 * 1024 + 1)
        resp = client.post(
            "/api/v1/gradient",
            data={"content": "https://example.com"},
            files={"logo": ("big.png", big_logo, "image/png")},
        )
        assert resp.status_code == 400
        assert "2 MB" in resp.json()["error"]

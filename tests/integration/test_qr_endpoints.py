"""Integration tests for QR code generation endpoints."""


class TestClassicEndpoint:
    def test_get(self, client):
        resp = client.get("/api/v1/classic", params={"content": "https://example.com"})
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        assert resp.content[:4] == b"\x89PNG"

    def test_post(self, client):
        resp = client.post("/api/v1/classic", params={"content": "hello"})
        assert resp.status_code == 200

    def test_colors(self, client):
        resp = client.get(
            "/api/v1/classic",
            params={"content": "test", "color": "#FF0000", "background": "#00FF00"},
        )
        assert resp.status_code == 200

    def test_size(self, client):
        resp = client.get("/api/v1/classic", params={"content": "test", "size": 200})
        assert resp.status_code == 200

    def test_missing_content(self, client):
        resp = client.get("/api/v1/classic")
        assert resp.status_code == 400

    def test_size_too_large(self, client):
        resp = client.get("/api/v1/classic", params={"content": "test", "size": 5000})
        assert resp.status_code == 400

    def test_size_too_small(self, client):
        resp = client.get("/api/v1/classic", params={"content": "test", "size": 5})
        assert resp.status_code == 400

    def test_invalid_color(self, client):
        resp = client.get(
            "/api/v1/classic", params={"content": "test", "color": "nope"}
        )
        assert resp.status_code == 400

    def test_circle_style(self, client):
        resp = client.get(
            "/api/v1/classic", params={"content": "test", "style": "circle"}
        )
        assert resp.status_code == 200

    def test_svg(self, client):
        resp = client.get(
            "/api/v1/classic", params={"content": "test", "output": "svg"}
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/svg+xml"
        assert b"<svg" in resp.content

    def test_all_styles(self, client):
        for s in [
            "rounded",
            "square",
            "circle",
            "gapped",
            "horizontal_bars",
            "vertical_bars",
        ]:
            resp = client.get("/api/v1/classic", params={"content": "test", "style": s})
            assert resp.status_code == 200, f"Failed for style: {s}"

    def test_request_id(self, client):
        resp = client.get("/api/v1/classic", params={"content": "test"})
        assert resp.headers["x-request-id"].startswith("req_")

    def test_cache_header(self, client):
        resp = client.get("/api/v1/classic", params={"content": "test"})
        assert "s-maxage" in resp.headers.get("cache-control", "")

    def test_logo(self, client):
        from PIL import Image
        import io

        img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        resp = client.post(
            "/api/v1/classic",
            params={"content": "https://example.com"},
            files={"logo": ("logo.png", buf.getvalue(), "image/png")},
        )
        assert resp.status_code == 200

    def test_wifi_content(self, client):
        """User passes pre-formatted WiFi string directly."""
        resp = client.get(
            "/api/v1/classic", params={"content": "WIFI:T:WPA;S:MyNet;P:secret;;"}
        )
        assert resp.status_code == 200


class TestGradientEndpoint:
    def test_get(self, client):
        resp = client.get("/api/v1/gradient", params={"content": "https://example.com"})
        assert resp.status_code == 200
        assert resp.content[:4] == b"\x89PNG"

    def test_colors(self, client):
        resp = client.get(
            "/api/v1/gradient",
            params={
                "content": "test",
                "start": "#ff0000",
                "end": "#0000ff",
                "background": "#ffffff",
            },
        )
        assert resp.status_code == 200

    def test_size(self, client):
        resp = client.get("/api/v1/gradient", params={"content": "test", "size": 300})
        assert resp.status_code == 200

    def test_missing_content(self, client):
        resp = client.get("/api/v1/gradient")
        assert resp.status_code == 400

    def test_horizontal(self, client):
        resp = client.get(
            "/api/v1/gradient", params={"content": "test", "direction": "horizontal"}
        )
        assert resp.status_code == 200

    def test_radial(self, client):
        resp = client.get(
            "/api/v1/gradient", params={"content": "test", "direction": "radial"}
        )
        assert resp.status_code == 200

    def test_svg_not_supported(self, client):
        resp = client.get(
            "/api/v1/gradient", params={"content": "test", "output": "svg"}
        )
        assert resp.status_code == 400
        assert "SVG" in resp.json()["error"]

    def test_logo(self, client):
        from PIL import Image
        import io

        img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        resp = client.post(
            "/api/v1/gradient",
            params={"content": "https://example.com"},
            files={"logo": ("logo.png", buf.getvalue(), "image/png")},
        )
        assert resp.status_code == 200


class TestBatchEndpoint:
    def test_basic(self, client):
        body = {
            "items": [
                {"content": "https://example.com"},
                {"content": "https://google.com", "color": "#FF0000"},
            ]
        }
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"

    def test_with_svg(self, client):
        body = {"items": [{"content": "test1", "output": "svg"}, {"content": "test2"}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200

    def test_empty(self, client):
        resp = client.post("/api/v1/batch", json={"items": []})
        assert resp.status_code == 400

    def test_too_many(self, client):
        body = {"items": [{"content": f"item{i}"} for i in range(21)]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 400

    def test_filenames(self, client):
        body = {"items": [{"content": "test", "filename": "my_qr"}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200

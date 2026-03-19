"""Integration tests for batch endpoint — filename sanitization and zip contents."""

import io
import zipfile


class TestBatchFilenames:
    def test_default_filenames(self, client):
        body = {"items": [{"content": "a"}, {"content": "b"}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        names = zf.namelist()
        assert "qrcode_1.png" in names
        assert "qrcode_2.png" in names

    def test_custom_filenames(self, client):
        body = {"items": [{"content": "test", "filename": "my_code"}]}
        resp = client.post("/api/v1/batch", json=body)
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        assert "my_code.png" in zf.namelist()

    def test_filename_sanitization_strips_path(self, client):
        body = {"items": [{"content": "test", "filename": "../../../etc/passwd"}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        names = zf.namelist()
        # No path traversal in zip entries
        for name in names:
            assert ".." not in name
            assert "/" not in name

    def test_filename_special_chars_sanitized(self, client):
        body = {"items": [{"content": "test", "filename": "my file@#$.png"}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        names = zf.namelist()
        assert len(names) == 1
        # Should not contain special chars except underscore, dash, dot
        name = names[0]
        assert "@" not in name
        assert "#" not in name
        assert "$" not in name

    def test_svg_batch_item(self, client):
        body = {"items": [{"content": "test", "output": "svg", "filename": "icon"}]}
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        names = zf.namelist()
        assert any(n.endswith(".svg") for n in names)

    def test_mixed_png_svg(self, client):
        body = {
            "items": [
                {"content": "a", "output": "png"},
                {"content": "b", "output": "svg"},
            ]
        }
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        names = zf.namelist()
        assert any(n.endswith(".png") for n in names)
        assert any(n.endswith(".svg") for n in names)

    def test_batch_with_styles(self, client):
        body = {
            "items": [
                {"content": "a", "style": "circle"},
                {"content": "b", "style": "gapped"},
            ]
        }
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200

    def test_batch_with_colors_and_size(self, client):
        body = {
            "items": [
                {
                    "content": "test",
                    "color": "#ff0000",
                    "background": "#00ff00",
                    "size": 200,
                }
            ]
        }
        resp = client.post("/api/v1/batch", json=body)
        assert resp.status_code == 200

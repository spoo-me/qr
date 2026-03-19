"""Integration tests for app factory — docs, CORS, OpenAPI."""

from unittest.mock import patch


class TestDocsEndpoint:
    def test_docs_returns_scalar_html_in_dev(self, client):
        resp = client.get("/docs", follow_redirects=False)
        assert resp.status_code == 200
        assert "api-reference" in resp.text
        assert "scalar" in resp.text.lower()

    def test_docs_redirects_in_production(self):
        with patch.dict("os.environ", {"ENV": "production"}):
            from app import create_app

            app = create_app()
            from fastapi.testclient import TestClient

            with TestClient(app) as c:
                resp = c.get("/docs", follow_redirects=False)
                assert resp.status_code == 307
                assert "docs.spoo.me" in resp.headers.get(
                    "location", ""
                ) or "spoo.me/docs" in resp.headers.get("location", "")


class TestCORS:
    def test_cors_allows_any_origin(self, client):
        resp = client.options(
            "/api/v1/classic",
            headers={
                "Origin": "https://spoo.me",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") == "*"

    def test_cors_no_credentials(self, client):
        resp = client.options(
            "/api/v1/classic",
            headers={
                "Origin": "https://spoo.me",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-credentials" not in resp.headers


class TestOpenAPI:
    def test_openapi_json(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "openapi" in data
        assert "paths" in data

    def test_openapi_has_classic_endpoint(self, client):
        data = client.get("/openapi.json").json()
        assert "/api/v1/classic" in data["paths"]

    def test_openapi_has_gradient_endpoint(self, client):
        data = client.get("/openapi.json").json()
        assert "/api/v1/gradient" in data["paths"]

    def test_openapi_has_batch_endpoint(self, client):
        data = client.get("/openapi.json").json()
        assert "/api/v1/batch" in data["paths"]

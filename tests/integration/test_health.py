"""Integration tests for GET /health."""


class TestHealthEndpoint:
    def test_get_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"

    def test_post_health_not_allowed(self, client):
        resp = client.post("/health")
        assert resp.status_code == 405

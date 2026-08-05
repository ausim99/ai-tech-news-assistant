from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import news

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_news_today_404_when_no_digest_yet(monkeypatch) -> None:
    async def fake_get_json_file(path: str):
        return None

    monkeypatch.setattr(news, "get_json_file", fake_get_json_file)

    resp = client.get("/api/news/today")
    assert resp.status_code == 404

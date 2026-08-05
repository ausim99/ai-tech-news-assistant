from datetime import UTC, datetime, timedelta

from agents.digest import _fallback_ranking
from agents.telegram import _escape
from agents.trend import _is_recent
from services.dedupe import dedupe
from services.notify.base import chunk_text


def test_dedupe_drops_near_identical_titles() -> None:
    items = [
        {"title": "OpenAI releases GPT-5"},
        {"title": "OpenAI Releases GPT-5!"},
        {"title": "NVIDIA announces new GPU"},
    ]
    result = dedupe(items)
    assert len(result) == 2


def test_chunk_text_respects_size_and_prefers_newline() -> None:
    text = "a" * 10 + "\n" + "b" * 10
    chunks = chunk_text(text, size=15)
    assert all(len(c) <= 15 for c in chunks)
    assert "".join(chunks) == text
    assert chunks[0] == "a" * 10  # split on the newline, not mid-word at size


def test_chunk_text_noop_when_under_size() -> None:
    assert chunk_text("short", size=100) == ["short"]


def test_telegram_escape_handles_markdown_special_chars() -> None:
    assert _escape("A_B*C`D[E") == "A\\_B\\*C\\`D\\[E"


def test_digest_fallback_ranking_splits_by_category() -> None:
    items = [
        {"link": "a", "category": "AI Research", "confidence": 0.9},
        {"link": "b", "category": "Tech Industry", "confidence": 0.8},
        {"link": "c", "category": "AI Product", "confidence": 0.7},
    ]
    ranking = _fallback_ranking(items)
    assert ranking["top_ai_news"] == ["a", "c"]
    assert ranking["top_tech_news"] == ["b"]


def test_is_recent_missing_date_is_lenient() -> None:
    assert _is_recent({}) is True


def test_is_recent_rejects_old_items() -> None:
    old = (datetime.now(UTC) - timedelta(days=5)).isoformat()
    assert _is_recent({"published_iso": old}) is False


def test_is_recent_accepts_fresh_items() -> None:
    fresh = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    assert _is_recent({"published_iso": fresh}) is True

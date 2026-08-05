"""Fetch and parse RSS/Atom feeds into a common item shape."""

import calendar
from datetime import UTC, datetime
from typing import Any

import feedparser
import httpx

from services.logging import logger


async def fetch_feed(url: str, timeout: float = 15.0) -> list[dict[str, Any]]:
    """Fetch one feed and return normalized entries. Empty list on any failure -
    a single dead source should never take down the whole pipeline."""
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "ai-tech-news-assistant/1.0"})
            resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning(f"feed fetch failed for {url}: {e}")
        return []

    parsed = feedparser.parse(resp.content)
    if parsed.bozo and not parsed.entries:
        logger.warning(f"feed parse failed for {url}: {parsed.get('bozo_exception')}")
        return []

    return [_normalize_entry(e, url) for e in parsed.entries]


def _to_iso(entry: Any) -> str:
    for key in ("published_parsed", "updated_parsed"):
        struct = entry.get(key)
        if struct:
            return datetime.fromtimestamp(calendar.timegm(struct), tz=UTC).isoformat()
    return ""


def _normalize_entry(entry: Any, source_url: str) -> dict[str, Any]:
    link = entry.get("link") or entry.get("id") or ""
    return {
        "title": (entry.get("title") or "").strip(),
        "link": link,
        "published": entry.get("published") or entry.get("updated") or "",
        "published_iso": _to_iso(entry),
        "summary": (entry.get("summary") or "").strip(),
        "author": entry.get("author", ""),
        "source_feed": source_url,
    }

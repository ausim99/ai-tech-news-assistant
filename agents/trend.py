"""Collect raw articles from configured RSS sources.

Sources are curated AI/tech feeds already scoped to the topic, so we don't
run a second keyword filter here - that would risk dropping legitimate
stories on a fragile heuristic. Off-topic drift, if any, gets sorted out by
the research agent's categorization and the digest agent's ranking.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from services import storage
from services.dedupe import dedupe
from services.logging import logger
from services.rss import fetch_feed

# 96h (4 days), not 24-30h: several legit sources (DeepMind, Azure blog, ...)
# post every few days rather than daily, and dropping their news entirely
# over a tight window would be worse than an occasional slightly-stale item.
# The digest agent ranks by importance, not just recency, so this is safe.
MAX_AGE_HOURS = 96


def _is_recent(item: dict[str, Any]) -> bool:
    iso = item.get("published_iso")
    if not iso:
        return True  # unknown date: be lenient, don't discard good items over missing metadata
    try:
        published = datetime.fromisoformat(iso)
    except ValueError:
        return True
    return datetime.now(UTC) - published <= timedelta(hours=MAX_AGE_HOURS)


async def collect() -> list[dict[str, Any]]:
    config = storage.load_config()
    sources = config.get("sources", [])

    active = [s for s in sources if s.get("rss_url")]
    skipped = [s["name"] for s in sources if not s.get("rss_url")]
    if skipped:
        logger.info(f"skipping sources with no RSS URL configured: {', '.join(skipped)}")

    results = await asyncio.gather(*(fetch_feed(s["rss_url"]) for s in active))

    items: list[dict[str, Any]] = []
    for source, entries in zip(active, results):
        for entry in entries:
            if not entry["title"] or not entry["link"] or not _is_recent(entry):
                continue
            items.append(
                {
                    **entry,
                    "source_name": source["name"],
                    "source_category": source.get("category", "Tech"),
                }
            )

    logger.info(f"collected {len(items)} raw items from {len(active)} sources")
    return dedupe(items)

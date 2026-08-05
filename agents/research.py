"""Extract structured, source-grounded facts from each collected article."""

import asyncio
import json
from typing import Any

from prompts.research import SYSTEM
from services.llm import LLMError, complete
from services.logging import logger

MIN_CONFIDENCE = 0.5


async def research_item(item: dict[str, Any]) -> dict[str, Any] | None:
    user = json.dumps(
        {
            "title": item["title"],
            "source": item["source_name"],
            "summary": item.get("summary", ""),
            "link": item["link"],
            "published": item.get("published_iso") or item.get("published", ""),
        },
        ensure_ascii=False,
    )

    try:
        raw = await complete(SYSTEM, user, json_mode=True)
        parsed = json.loads(raw)
    except (LLMError, json.JSONDecodeError) as e:
        logger.warning(f"research failed for '{item['title']}': {e}")
        return None

    if parsed.get("confidence", 0) < MIN_CONFIDENCE:
        logger.info(f"dropping low-confidence item: {item['title']} ({parsed.get('confidence')})")
        return None

    return {**parsed, "link": item["link"], "source": item["source_name"]}


async def research_all(items: list[dict[str, Any]], concurrency: int = 5) -> list[dict[str, Any]]:
    sem = asyncio.Semaphore(concurrency)

    async def _bound(item: dict[str, Any]) -> dict[str, Any] | None:
        async with sem:
            return await research_item(item)

    results = await asyncio.gather(*(_bound(i) for i in items))
    researched = [r for r in results if r is not None]
    logger.info(f"researched {len(researched)}/{len(items)} items")
    return researched

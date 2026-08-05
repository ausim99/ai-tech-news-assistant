"""Generate a practical how-to tutorial for each researched news item.

ponytail: capped by `max_items` (driven by data/config.json's
max_tutorial_items) to bound LLM spend - the pipeline researches every
collected item, but full step-by-step tutorials are only worth generating
for the top N by research confidence. Raise the cap in config if needed.
"""

import asyncio
import json
from typing import Any

from prompts.tutorial import SYSTEM
from services.llm import LLMError, complete
from services.logging import logger

DEFAULT_MAX_ITEMS = 25


async def tutorial_for_item(item: dict[str, Any]) -> dict[str, Any] | None:
    user = json.dumps(
        {
            "title": item["title"],
            "summary": item["summary"],
            "key_facts": item.get("key_facts", []),
            "source": item["source"],
            "link": item["link"],
        },
        ensure_ascii=False,
    )

    try:
        raw = await complete(SYSTEM, user, json_mode=True)
        return json.loads(raw)
    except (LLMError, json.JSONDecodeError) as e:
        logger.warning(f"tutorial generation failed for '{item['title']}': {e}")
        return None


async def generate_all(
    items: list[dict[str, Any]], max_items: int = DEFAULT_MAX_ITEMS, concurrency: int = 5
) -> list[dict[str, Any]]:
    ranked = sorted(items, key=lambda i: i.get("confidence", 0), reverse=True)
    to_process, rest = ranked[:max_items], ranked[max_items:]

    sem = asyncio.Semaphore(concurrency)

    async def _bound(item: dict[str, Any]) -> dict[str, Any] | None:
        async with sem:
            return await tutorial_for_item(item)

    tutorials = await asyncio.gather(*(_bound(i) for i in to_process))
    processed = [{**item, "tutorial": t} for item, t in zip(to_process, tutorials)]
    skipped = [{**item, "tutorial": None} for item in rest]
    return processed + skipped

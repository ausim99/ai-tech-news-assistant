"""Translate researched items into natural Bangla."""

import asyncio
import json
from typing import Any

from prompts.translate import SYSTEM
from services.llm import LLMError, complete
from services.logging import logger


async def translate_item(item: dict[str, Any]) -> dict[str, Any]:
    user = json.dumps(
        {
            "title": item["title"],
            "summary": item["summary"],
            "key_facts": item.get("key_facts", []),
            "future_impact": item.get("future_impact", ""),
        },
        ensure_ascii=False,
    )

    try:
        raw = await complete(SYSTEM, user, json_mode=True)
        bn = json.loads(raw)
    except (LLMError, json.JSONDecodeError) as e:
        logger.warning(f"translation failed for '{item['title']}', keeping English: {e}")
        bn = {"title_bn": item["title"], "summary_bn": item["summary"], "why_it_matters_bn": ""}

    return {**item, **bn}


async def translate_all(items: list[dict[str, Any]], concurrency: int = 5) -> list[dict[str, Any]]:
    sem = asyncio.Semaphore(concurrency)

    async def _bound(item: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            return await translate_item(item)

    return list(await asyncio.gather(*(_bound(i) for i in items)))

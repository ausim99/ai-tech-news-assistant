"""Rank researched+translated items into the daily digest via the LLM, then
assemble the final structure stored to data/daily/{date}.json."""

import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from prompts.digest import SYSTEM
from services.llm import LLMError, complete
from services.logging import logger

DHAKA = ZoneInfo("Asia/Dhaka")


def _fallback_ranking(items: list[dict[str, Any]]) -> dict[str, list[str]]:
    ranked = sorted(items, key=lambda i: i.get("confidence", 0), reverse=True)
    ai = [i["link"] for i in ranked if i.get("category", "").startswith("AI")]
    tech = [i["link"] for i in ranked if not i.get("category", "").startswith("AI")]
    return {"top_ai_news": ai[:10], "top_tech_news": tech[:5]}


async def build_digest(items: list[dict[str, Any]]) -> dict[str, Any]:
    by_link = {item["link"]: item for item in items}
    slim = [
        {
            "link": i["link"],
            "title": i["title"],
            "category": i.get("category", ""),
            "summary": i["summary"],
        }
        for i in items
    ]

    extras = {
        "top_ai_news": [],
        "top_tech_news": [],
        "ai_tip_bn": "",
        "prompt_of_the_day_bn": "",
        "automation_idea_bn": "",
        "learning_resource_bn": "",
        "free_ai_tool_bn": "",
        "youtube_recommendation_bn": "",
        "productivity_tip_bn": "",
    }
    try:
        raw = await complete(SYSTEM, json.dumps(slim, ensure_ascii=False), json_mode=True)
        extras.update(json.loads(raw))
    except (LLMError, json.JSONDecodeError) as e:
        logger.warning(f"digest ranking failed, falling back to confidence order: {e}")
        extras.update(_fallback_ranking(items))

    return {
        "date": datetime.now(DHAKA).strftime("%Y-%m-%d"),
        "generated_at": datetime.now(DHAKA).isoformat(),
        "top_ai_news": [by_link[link] for link in extras["top_ai_news"] if link in by_link],
        "top_tech_news": [by_link[link] for link in extras["top_tech_news"] if link in by_link],
        "ai_tip": extras["ai_tip_bn"],
        "prompt_of_the_day": extras["prompt_of_the_day_bn"],
        "automation_idea": extras["automation_idea_bn"],
        "learning_resource": extras["learning_resource_bn"],
        "free_ai_tool": extras["free_ai_tool_bn"],
        "youtube_recommendation": extras["youtube_recommendation_bn"],
        "productivity_tip": extras["productivity_tip_bn"],
        "items": items,
    }

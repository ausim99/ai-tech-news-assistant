"""Format the daily digest into a WhatsApp-friendly message and send it.

Lighter than the Telegram version (top items + one tip, no per-item
"why it matters" or extras block) since WhatsApp readers expect a shorter
message; long-message splitting is handled by the transport layer
(services/notify/whatsapp.py).
"""

from typing import Any

from services.logging import logger
from services.notify import whatsapp as whatsapp_client


def _format_item(item: dict[str, Any], index: int) -> str:
    lines = [
        f"{index}. *{item.get('title_bn') or item['title']}*",
        f"উৎস: {item['source']}",
        item.get("summary_bn") or item["summary"],
        item["link"],
    ]
    return "\n".join(lines)


def format_digest(digest: dict[str, Any]) -> str:
    parts = [f"*আজকের AI ও টেক সংবাদ* - {digest['date']}"]

    if digest["top_ai_news"]:
        parts.append("*শীর্ষ AI সংবাদ*")
        parts.extend(_format_item(item, i + 1) for i, item in enumerate(digest["top_ai_news"]))

    if digest["top_tech_news"]:
        parts.append("*শীর্ষ টেক সংবাদ*")
        parts.extend(_format_item(item, i + 1) for i, item in enumerate(digest["top_tech_news"]))

    if digest.get("ai_tip"):
        parts.append(f"💡 আজকের টিপ: {digest['ai_tip']}")

    return "\n\n".join(parts)


async def send_digest(digest: dict[str, Any]) -> None:
    await whatsapp_client.send(format_digest(digest))
    logger.info("digest sent to WhatsApp")

"""Format the daily digest into a Telegram message (legacy Markdown) and send it."""

from typing import Any

from services.logging import logger
from services.notify import telegram as telegram_client

CATEGORY_EMOJI = {
    "AI Research": "🔬",
    "AI Product": "🤖",
    "Tech Industry": "🏢",
    "Open Source": "🧩",
    "Hardware": "💻",
    "Policy": "⚖️",
    "Other": "📰",
}

# Telegram's legacy "Markdown" parse mode only needs these escaped.
_MD_SPECIAL = ("_", "*", "`", "[")


def _escape(text: str) -> str:
    for ch in _MD_SPECIAL:
        text = text.replace(ch, f"\\{ch}")
    return text


def _format_item(item: dict[str, Any], index: int) -> str:
    emoji = CATEGORY_EMOJI.get(item.get("category", ""), "📰")
    title = _escape(item.get("title_bn") or item["title"])
    source = _escape(item["source"])
    summary = _escape(item.get("summary_bn") or item["summary"])

    lines = [f"{emoji} *{index}. {title}*", f"_উৎস: {source}_", summary]
    if item.get("why_it_matters_bn"):
        lines.append(f"*কেন গুরুত্বপূর্ণ:* {_escape(item['why_it_matters_bn'])}")
    lines.append(f"[আরও পড়ুন]({item['link']})")
    return "\n".join(lines)


def format_digest(digest: dict[str, Any]) -> str:
    parts = [f"🗞️ *আজকের AI ও টেক সংবাদ* — {digest['date']}"]

    if digest["top_ai_news"]:
        parts.append("*🤖 শীর্ষ AI সংবাদ*")
        parts.extend(_format_item(item, i + 1) for i, item in enumerate(digest["top_ai_news"]))

    if digest["top_tech_news"]:
        parts.append("*💻 শীর্ষ টেক সংবাদ*")
        parts.extend(_format_item(item, i + 1) for i, item in enumerate(digest["top_tech_news"]))

    extras = [
        ("💡 আজকের AI টিপ", digest.get("ai_tip")),
        ("✍️ আজকের প্রম্পট", digest.get("prompt_of_the_day")),
        ("⚙️ অটোমেশন আইডিয়া", digest.get("automation_idea")),
        ("📚 শেখার রিসোর্স", digest.get("learning_resource")),
        ("🆓 ফ্রি AI টুল", digest.get("free_ai_tool")),
        ("📺 ইউটিউব সাজেশন", digest.get("youtube_recommendation")),
        ("⏱️ প্রোডাক্টিভিটি টিপ", digest.get("productivity_tip")),
    ]
    extra_lines = [f"*{label}:* {_escape(value)}" for label, value in extras if value]
    if extra_lines:
        parts.append("*✨ আজকের এক্সট্রা*\n" + "\n".join(extra_lines))

    return "\n\n".join(parts)


async def send_digest(digest: dict[str, Any]) -> None:
    await telegram_client.send(format_digest(digest))
    logger.info("digest sent to Telegram")

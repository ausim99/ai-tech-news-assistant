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
CATEGORY_BN = {
    "AI Research": "AI গবেষণা",
    "AI Product": "AI প্রোডাক্ট",
    "Tech Industry": "টেক ইন্ডাস্ট্রি",
    "Open Source": "ওপেন সোর্স",
    "Hardware": "হার্ডওয়্যার",
    "Policy": "নীতি",
    "Other": "অন্যান্য",
}

# Telegram's legacy "Markdown" parse mode only needs these escaped.
_MD_SPECIAL = ("_", "*", "`", "[")


def _escape(text: str) -> str:
    for ch in _MD_SPECIAL:
        text = text.replace(ch, f"\\{ch}")
    return text


def _bullets(label: str, items: list[str]) -> str | None:
    if not items:
        return None
    lines = "\n".join(f"• {_escape(v)}" for v in items)
    return f"*{label}:*\n{lines}"


def _format_tutorial(tutorial: dict[str, Any]) -> list[str]:
    lines = []
    if tutorial.get("what_happened"):
        lines.append(f"*🎯 বিস্তারিত:* {_escape(tutorial['what_happened'])}")
    if tutorial.get("real_world_example"):
        lines.append(f"*🌍 বাস্তব উদাহরণ:* {_escape(tutorial['real_world_example'])}")
    if tutorial.get("who_should_care"):
        lines.append(f"*👥 কাদের জন্য প্রযোজ্য:* {_escape(tutorial['who_should_care'])}")
    steps = _bullets("✅ যেভাবে চেষ্টা করবেন", tutorial.get("steps", []))
    if steps:
        lines.append(steps)
    pros = _bullets("👍 সুবিধা", tutorial.get("advantages", []))
    if pros:
        lines.append(pros)
    cons = _bullets("👎 অসুবিধা", tutorial.get("disadvantages", []))
    if cons:
        lines.append(cons)
    if tutorial.get("future_impact"):
        lines.append(f"*🔭 ভবিষ্যৎ প্রভাব:* {_escape(tutorial['future_impact'])}")
    resources = _bullets("📚 শেখার রিসোর্স", tutorial.get("learning_resources", []))
    if resources:
        lines.append(resources)
    repos = _bullets("🐙 GitHub", tutorial.get("github_repos", []))
    if repos:
        lines.append(repos)
    return lines


def _format_item(item: dict[str, Any], index: int) -> str:
    emoji = CATEGORY_EMOJI.get(item.get("category", ""), "📰")
    category_bn = CATEGORY_BN.get(item.get("category", ""), "")
    title = _escape(item.get("title_bn") or item["title"])
    source = _escape(item["source"])
    summary = _escape(item.get("summary_bn") or item["summary"])

    lines = [f"{emoji} *{index}. {title}*", f"_উৎস: {source} | বিভাগ: {category_bn}_", summary]
    if item.get("why_it_matters_bn"):
        lines.append(f"*কেন গুরুত্বপূর্ণ:* {_escape(item['why_it_matters_bn'])}")
    if item.get("tutorial"):
        lines.extend(_format_tutorial(item["tutorial"]))
    lines.append(f"🔗 [মূল সংবাদ পড়ুন]({item['link']})")
    return "\n".join(lines)


def format_digest(digest: dict[str, Any]) -> str:
    shown = len(digest["top_ai_news"]) + len(digest["top_tech_news"])
    analyzed = len(digest.get("items", [])) or shown
    header = (
        f"🗞️ *আজকের AI ও টেক সংবাদ* — {digest['date']}\n"
        f"📊 {analyzed} টি সংবাদ বিশ্লেষণ করে সেরা {shown} টি বাছাই করা হয়েছে"
    )
    parts = [
        header,
    ]

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

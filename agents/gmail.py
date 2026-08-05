"""Format the daily digest into an HTML email and send it via Gmail."""

from html import escape
from typing import Any

from services.logging import logger
from services.notify import gmail as gmail_client

CATEGORY_EMOJI = {
    "AI Research": "🔬",
    "AI Product": "🤖",
    "Tech Industry": "🏢",
    "Open Source": "🧩",
    "Hardware": "💻",
    "Policy": "⚖️",
    "Other": "📰",
}


def _format_item(item: dict[str, Any]) -> str:
    emoji = CATEGORY_EMOJI.get(item.get("category", ""), "📰")
    title = escape(item.get("title_bn") or item["title"])
    source = escape(item["source"])
    summary = escape(item.get("summary_bn") or item["summary"])
    link = escape(item["link"])

    why_html = ""
    if item.get("why_it_matters_bn"):
        why_html = f"<p><b>কেন গুরুত্বপূর্ণ:</b> {escape(item['why_it_matters_bn'])}</p>"

    return f"""
    <div style="margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #e2e8f0;">
      <h3 style="margin:0 0 4px;">{emoji} {title}</h3>
      <p style="color:#64748b;font-size:13px;margin:0 0 8px;">উৎস: {source}</p>
      <p style="margin:0 0 8px;">{summary}</p>
      {why_html}
      <a href="{link}">আরও পড়ুন →</a>
    </div>
    """


def format_digest(digest: dict[str, Any]) -> tuple[str, str]:
    subject = f"AI ও টেক সংবাদ - {digest['date']}"
    parts = [f"<h1>🗞️ আজকের AI ও টেক সংবাদ</h1><p>{escape(digest['date'])}</p>"]

    if digest["top_ai_news"]:
        parts.append("<h2>🤖 শীর্ষ AI সংবাদ</h2>")
        parts.extend(_format_item(item) for item in digest["top_ai_news"])

    if digest["top_tech_news"]:
        parts.append("<h2>💻 শীর্ষ টেক সংবাদ</h2>")
        parts.extend(_format_item(item) for item in digest["top_tech_news"])

    extras = [
        ("💡 আজকের AI টিপ", digest.get("ai_tip")),
        ("✍️ আজকের প্রম্পট", digest.get("prompt_of_the_day")),
        ("⚙️ অটোমেশন আইডিয়া", digest.get("automation_idea")),
        ("📚 শেখার রিসোর্স", digest.get("learning_resource")),
        ("🆓 ফ্রি AI টুল", digest.get("free_ai_tool")),
        ("📺 ইউটিউব সাজেশন", digest.get("youtube_recommendation")),
        ("⏱️ প্রোডাক্টিভিটি টিপ", digest.get("productivity_tip")),
    ]
    extra_html = "".join(
        f"<p><b>{label}:</b> {escape(value)}</p>" for label, value in extras if value
    )
    if extra_html:
        parts.append(f"<h2>✨ আজকের এক্সট্রা</h2>{extra_html}")

    html_body = f'<div style="font-family:sans-serif;max-width:640px;">{"".join(parts)}</div>'
    return subject, html_body


async def send_digest(digest: dict[str, Any]) -> None:
    subject, html_body = format_digest(digest)
    await gmail_client.send(subject, html_body)
    logger.info("digest sent via Gmail")

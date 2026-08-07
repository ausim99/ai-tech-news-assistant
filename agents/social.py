"""Format the daily digest into a short social caption and post it to
LinkedIn/Facebook. Each platform is entirely optional (skipped if its
tokens aren't set) and failures on one don't block the other or the
rest of the pipeline - this runs after Telegram/Gmail delivery, which
is the primary channel."""

from typing import Any

from services.config import get_settings
from services.logging import logger
from services.notify import facebook as facebook_client
from services.notify import linkedin as linkedin_client
from services.notify.facebook import FacebookSendError
from services.notify.linkedin import LinkedInSendError

MAX_ITEMS = 6
MAX_LEN = 2900  # safety margin under LinkedIn's ~3000-char commentary limit


def format_post(digest: dict[str, Any]) -> str:
    combined = (digest.get("top_ai_news", []) + digest.get("top_tech_news", []))[:MAX_ITEMS]

    lines = [f"AI ও টেক সংবাদ — {digest['date']}", ""]
    for item in combined:
        title = item.get("title_bn") or item["title"]
        lines.append(f"🔹 {title}")
        lines.append(item["link"])
        lines.append("")
    lines.append("#AI #TechNews #ArtificialIntelligence")

    return "\n".join(lines).strip()[:MAX_LEN]


async def send_post(digest: dict[str, Any]) -> None:
    settings = get_settings()
    text = format_post(digest)

    if settings.linkedin_access_token and settings.linkedin_author_urn:
        try:
            await linkedin_client.send(text)
            logger.info("digest posted to LinkedIn")
        except LinkedInSendError as e:
            logger.warning(f"LinkedIn post failed: {e}")

    if settings.facebook_page_id and settings.facebook_page_access_token:
        try:
            await facebook_client.send(text)
            logger.info("digest posted to Facebook")
        except FacebookSendError as e:
            logger.warning(f"Facebook post failed: {e}")

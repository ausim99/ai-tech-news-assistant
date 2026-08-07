"""Facebook Page Graph API delivery.

ponytail: page access token should be generated as a long-lived token
(~60 days) or, better, a System User token via Business Manager for
one that doesn't expire. Upgrade to token-refresh automation if manual
regeneration becomes a chore.
"""

import httpx

from services.config import get_settings

GRAPH_VERSION = "v21.0"


class FacebookSendError(RuntimeError):
    pass


async def send(text: str) -> None:
    settings = get_settings()
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{settings.facebook_page_id}/feed"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            url, data={"message": text, "access_token": settings.facebook_page_access_token}
        )
    if resp.is_error:
        raise FacebookSendError(f"Facebook post failed: {resp.status_code} {resp.text}")

"""LinkedIn Posts API (organic share) delivery.

ponytail: access token expires ~60 days (LinkedIn's Standard products
don't issue refresh tokens for member auth) - needs a manual re-auth
when it dies. Upgrade to a refresh-token-capable product if that
becomes annoying.
"""

import httpx

from services.config import get_settings

LINKEDIN_API_URL = "https://api.linkedin.com/rest/posts"
LINKEDIN_VERSION = "202607"


class LinkedInSendError(RuntimeError):
    pass


async def send(text: str) -> None:
    settings = get_settings()
    headers = {
        "Authorization": f"Bearer {settings.linkedin_access_token}",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    payload = {
        "author": settings.linkedin_author_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(LINKEDIN_API_URL, json=payload, headers=headers)
    if resp.is_error:
        raise LinkedInSendError(f"LinkedIn post failed: {resp.status_code} {resp.text}")

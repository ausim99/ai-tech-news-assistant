"""Meta WhatsApp Cloud API delivery.

Kept behind the same send(text) contract as telegram.py (see base.py) so a
different WhatsApp provider (Twilio, etc.) can replace this module without
touching agents/whatsapp.py or the caller.
"""

import httpx

from services.config import get_settings
from services.notify.base import chunk_text

GRAPH_API_VERSION = "v21.0"
MAX_LEN = 4096


class WhatsAppSendError(RuntimeError):
    pass


async def send(text: str) -> None:
    settings = get_settings()
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{settings.whatsapp_phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}

    async with httpx.AsyncClient(timeout=15) as client:
        for chunk in chunk_text(text, MAX_LEN):
            resp = await client.post(
                url,
                headers=headers,
                json={
                    "messaging_product": "whatsapp",
                    "to": settings.whatsapp_to_number,
                    "type": "text",
                    "text": {"body": chunk, "preview_url": True},
                },
            )
            if resp.is_error:
                raise WhatsAppSendError(f"WhatsApp send failed: {resp.status_code} {resp.text}")

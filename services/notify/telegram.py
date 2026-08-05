"""Telegram Bot API delivery."""

import httpx

from services.config import get_settings
from services.notify.base import chunk_text

MAX_LEN = 4096


class TelegramSendError(RuntimeError):
    pass


async def send(text: str) -> None:
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    async with httpx.AsyncClient(timeout=15) as client:
        for chunk in chunk_text(text, MAX_LEN):
            resp = await client.post(
                url,
                json={
                    "chat_id": settings.telegram_chat_id,
                    "text": chunk,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False,
                },
            )
            if resp.is_error:
                raise TelegramSendError(f"Telegram send failed: {resp.status_code} {resp.text}")

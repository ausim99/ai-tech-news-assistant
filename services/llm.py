"""Async client for the xAI Grok API (OpenAI-compatible chat completions)."""

import httpx

from services.config import get_settings
from services.logging import logger

GROK_API_URL = "https://api.x.ai/v1/chat/completions"


class LLMError(RuntimeError):
    """Raised when the Grok API call fails after all retries."""


async def complete(system: str, user: str, *, json_mode: bool = False, max_retries: int = 2) -> str:
    settings = get_settings()
    payload: dict = {
        "model": settings.grok_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {"Authorization": f"Bearer {settings.grok_api_key}"}

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(GROK_API_URL, json=payload, headers=headers)
            if resp.is_error:
                logger.warning(f"grok error body: {resp.text}")
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as e:
            last_error = e
            logger.warning(f"grok call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")

    raise LLMError(f"Grok API failed after {max_retries + 1} attempts: {last_error}")

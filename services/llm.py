"""Async client for chat-completion LLM providers, tried in order until one
works. All three speak the OpenAI-compatible chat completions shape:
Grok (primary) -> DeepSeek -> Gemini (via its OpenAI-compat endpoint)."""

import httpx

from services.config import get_settings
from services.logging import logger


class LLMError(RuntimeError):
    """Raised when every configured provider fails."""


def _providers() -> list[tuple[str, str, str, str]]:
    """(name, url, api_key, model) for each provider with a key set, in fallback order."""
    settings = get_settings()
    candidates = [
        ("grok", "https://api.x.ai/v1/chat/completions", settings.grok_api_key, settings.grok_model),
        ("deepseek", "https://api.deepseek.com/chat/completions", settings.deepseek_api_key, settings.deepseek_model),
        (
            "gemini",
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            settings.gemini_api_key,
            settings.gemini_model,
        ),
    ]
    return [c for c in candidates if c[2]]


async def _call(url: str, api_key: str, model: str, system: str, user: str, json_mode: bool) -> str:
    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload, headers={"Authorization": f"Bearer {api_key}"})
    if resp.is_error:
        logger.warning(f"llm error body: {resp.text}")
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


async def complete(system: str, user: str, *, json_mode: bool = False, max_retries: int = 2) -> str:
    providers = _providers()
    if not providers:
        raise LLMError("No LLM provider configured (set GROK_API_KEY, DEEPSEEK_API_KEY, or GEMINI_API_KEY)")

    last_error: Exception | None = None
    for name, url, api_key, model in providers:
        for attempt in range(max_retries + 1):
            try:
                return await _call(url, api_key, model, system, user, json_mode)
            except (httpx.HTTPError, KeyError, IndexError) as e:
                last_error = e
                logger.warning(f"{name} call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
        logger.warning(f"{name} exhausted retries, falling back to next provider")

    raise LLMError(f"All LLM providers failed: {last_error}")

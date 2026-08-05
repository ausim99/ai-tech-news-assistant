"""Lightweight reachability check for external dependencies. Run hourly by
healthcheck.yml; a non-zero exit triggers the Telegram failure alert."""

import asyncio
import sys

import httpx

from services import storage
from services.config import get_settings
from services.logging import logger
from services.notify import gmail as gmail_client


async def check_rss_sources() -> tuple[int, int]:
    config = storage.load_config()
    sources = [s for s in config.get("sources", []) if s.get("rss_url")]

    async def _check(source: dict) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(
                    source["rss_url"], headers={"User-Agent": "ai-tech-news-assistant/1.0"}
                )
            return resp.status_code < 400
        except httpx.HTTPError:
            return False

    results = await asyncio.gather(*(_check(s) for s in sources))
    for source, healthy in zip(sources, results):
        if not healthy:
            logger.warning(f"source unreachable: {source['name']}")
    return sum(results), len(sources)


async def check_telegram() -> bool:
    settings = get_settings()
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set")
        return False
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
    return resp.status_code == 200


async def check_gmail() -> bool:
    settings = get_settings()
    if not settings.gmail_address or not settings.gmail_app_password:
        logger.warning("Gmail credentials not set")
        return False
    return await gmail_client.verify_login()


async def main() -> None:
    ok_sources, total_sources = await check_rss_sources()
    telegram_ok = await check_telegram()
    gmail_ok = await check_gmail()

    logger.info(f"RSS sources reachable: {ok_sources}/{total_sources}")
    logger.info(f"Telegram: {'ok' if telegram_ok else 'FAILED'}")
    logger.info(f"Gmail: {'ok' if gmail_ok else 'FAILED'}")

    critical_failure = not telegram_ok or not gmail_ok
    widespread_source_outage = total_sources > 0 and ok_sources < total_sources / 2

    if critical_failure or widespread_source_outage:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

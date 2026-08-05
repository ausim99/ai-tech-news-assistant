"""Entry point for the daily pipeline. Invoked by GitHub Actions
(pipeline.yml / manual-run.yml via the run-pipeline composite action)."""

import argparse
import asyncio
import sys
from datetime import UTC, datetime

from agents import digest as digest_agent
from agents import research as research_agent
from agents import telegram as telegram_agent
from agents import translator as translator_agent
from agents import trend as trend_agent
from agents import tutorial as tutorial_agent
from agents import whatsapp as whatsapp_agent
from services import storage
from services.logging import logger


def _log_run(status: str, item_count: int) -> None:
    storage.append_log(
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": status,
            "item_count": item_count,
        }
    )


async def _run(skip_send: bool, dry_run: bool, resend_only: bool) -> None:
    if resend_only:
        digest = storage.read_json(f"daily/{storage.today_str()}.json")
        if digest is None:
            logger.error("resend-only requested but no digest exists for today")
            sys.exit(1)
    else:
        raw_items = await trend_agent.collect()
        if not raw_items:
            logger.warning("no items collected from any source, aborting")
            _log_run(status="empty", item_count=0)
            return

        researched = await research_agent.research_all(raw_items)
        translated = await translator_agent.translate_all(researched)

        config = storage.load_config()
        with_tutorials = await tutorial_agent.generate_all(
            translated, max_items=config.get("max_tutorial_items", tutorial_agent.DEFAULT_MAX_ITEMS)
        )
        digest = await digest_agent.build_digest(with_tutorials)

        if not dry_run:
            storage.write_json(f"daily/{digest['date']}.json", digest)
            storage.append_history(digest)

    if not skip_send:
        await telegram_agent.send_digest(digest)
        await whatsapp_agent.send_digest(digest)

    if not dry_run:
        _log_run(status="ok", item_count=len(digest.get("items", [])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-send", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resend-only", action="store_true")
    args = parser.parse_args()

    asyncio.run(_run(args.skip_send, args.dry_run, args.resend_only))


if __name__ == "__main__":
    main()

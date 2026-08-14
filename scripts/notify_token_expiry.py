"""Daily LinkedIn token-expiry reminder, run by token-reminder.yml.

Pings the owner on Telegram and Gmail every day once the LinkedIn access
token is inside its final 7 days (or past its ~60-day expiry), until the
token is rotated. Rotation is detected by comparing a stored SHA-256 hash
of the token value against the current one.
"""

import asyncio
from datetime import UTC, date, datetime

from services import storage
from services.config import get_settings
from services.logging import logger
from services.notify import gmail as gmail_client
from services.notify import telegram as telegram_client
from services.token_expiry import evaluate, expiry_dates


def _telegram_text(action: str, days_left: int, expiry: str) -> str:
    if action == "expired":
        return (
            "🔑 *LinkedIn access token has expired*\n\n"
            "The token passed its 60-day lifetime, so the daily digest is no "
            "longer posting to LinkedIn.\n\n"
            "Rotate it and update `LINKEDIN_ACCESS_TOKEN` / `LINKEDIN_AUTHOR_URN` "
            "in the GitHub repo secrets."
        )
    return (
        "🔑 *LinkedIn access token expiring soon*\n\n"
        f"Expires in ~{days_left} day(s) (on {expiry}).\n\n"
        "Rotate it and update `LINKEDIN_ACCESS_TOKEN` / `LINKEDIN_AUTHOR_URN` "
        "in the GitHub repo secrets to keep the daily digest posting."
    )


def _email_html(action: str, days_left: int, expiry: str) -> str:
    if action == "expired":
        status = "has expired"
    else:
        status = f"expires in ~{days_left} day(s) (on {expiry})"
    return (
        "<h3>LinkedIn access token reminder</h3>"
        f"<p>Your LinkedIn access token {status}.</p>"
        "<p>Rotate it and update <code>LINKEDIN_ACCESS_TOKEN</code> and "
        "<code>LINKEDIN_AUTHOR_URN</code> in the GitHub repo secrets so the "
        "daily digest keeps posting.</p>"
    )


async def main() -> None:
    settings = get_settings()
    today = datetime.now(UTC).date()

    existing = storage.read_json("linkedin_token.json", default=None)
    new_state, action = evaluate(settings.linkedin_access_token, today, existing)

    if new_state is None:
        logger.info("LinkedIn token not configured, skipping reminder")
        return
    storage.write_json("linkedin_token.json", new_state)

    if action is None:
        logger.info("LinkedIn token is healthy, no reminder needed")
        return

    expiry, _ = expiry_dates(date.fromisoformat(new_state["set_at"]))
    days_left = (expiry - today).days
    subject = (
        "LinkedIn access token has expired"
        if action == "expired"
        else "LinkedIn access token expiring soon"
    )

    if settings.telegram_bot_token and settings.telegram_chat_id:
        try:
            await telegram_client.send(_telegram_text(action, days_left, expiry.isoformat()))
            logger.info("sent LinkedIn token reminder via Telegram")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Telegram token reminder failed: {e}")

    if settings.gmail_address and settings.gmail_app_password:
        try:
            await gmail_client.send(subject, _email_html(action, days_left, expiry.isoformat()))
            logger.info("sent LinkedIn token reminder via Gmail")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Gmail token reminder failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

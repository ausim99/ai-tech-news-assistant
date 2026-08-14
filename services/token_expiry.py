"""LinkedIn access-token expiry tracking and reminder scheduling.

LinkedIn member access tokens expire after ~60 days and Standard products
don't issue refresh tokens, so the token has to be rotated by hand. We hash
the token value to detect rotation and, once the token is inside its final
7 days, tell the reminder script to ping the owner every day until it's
rotated.
"""

import hashlib
from datetime import date, timedelta
from typing import Any

TOKEN_TTL_DAYS = 60
WARN_BEFORE_DAYS = 7


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def expiry_dates(set_at: date) -> tuple[date, date]:
    """Return ``(expiry_date, first_warning_date)`` for a token set on ``set_at``."""
    expiry = set_at + timedelta(days=TOKEN_TTL_DAYS)
    return expiry, expiry - timedelta(days=WARN_BEFORE_DAYS)


def evaluate(
    token: str | None, today: date, existing: dict[str, Any] | None
) -> tuple[dict[str, Any] | None, str | None]:
    """Decide whether to notify about token expiry and compute the new state.

    Returns ``(new_state, action)`` where ``action`` is ``None`` (no message),
    ``"remind"`` (inside the final 7 days) or ``"expired"`` (past the 60-day
    TTL). ``new_state`` is the state dict to persist, or ``None`` when no
    token is configured.
    """
    if not token:
        return None, None

    token_hash = hash_token(token)

    if existing is None or existing.get("token_hash") != token_hash:
        return (
            {"token_hash": token_hash, "set_at": today.isoformat(), "last_reminder_at": None},
            None,
        )

    set_at = date.fromisoformat(existing["set_at"])
    expiry, warning = expiry_dates(set_at)

    if today >= expiry:
        action = "expired"
    elif today >= warning:
        action = "remind"
    else:
        action = None

    if action and existing.get("last_reminder_at") == today.isoformat():
        action = None

    new_state = dict(existing)
    if action:
        new_state["last_reminder_at"] = today.isoformat()

    return new_state, action

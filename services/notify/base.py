"""Shared contract + helpers for outbound delivery channels.

Callers depend on this Protocol, not on a specific channel's API, so adding
or swapping a channel is a drop-in module with a `send` function - nothing
else in the codebase changes. `chunk_text` is used by channels with a
message-length limit (Telegram); Gmail has no such limit so it doesn't need it.
"""

from typing import Protocol


class NotifyProvider(Protocol):
    async def send(self, text: str) -> None: ...


def chunk_text(text: str, size: int) -> list[str]:
    """Split text into <= size chunks, preferring to break on a newline."""
    if len(text) <= size:
        return [text]
    chunks = []
    while text:
        if len(text) <= size:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, size)
        if split_at <= 0:
            split_at = size
        chunks.append(text[:split_at])
        text = text[split_at:]
    return chunks

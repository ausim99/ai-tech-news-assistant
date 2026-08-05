"""Dedupe near-identical articles by normalized title similarity.

ponytail: O(n^2) pairwise comparison over the normalized titles - fine at the
scale of a few hundred items/day. Upgrade to embedding-based dedup if the
source list grows an order of magnitude.
"""

import re
from difflib import SequenceMatcher
from typing import Any

_PUNCT = re.compile(r"[^\w\s]")
_WS = re.compile(r"\s+")


def _normalize(title: str) -> str:
    return _WS.sub(" ", _PUNCT.sub("", title.lower())).strip()


def dedupe(items: list[dict[str, Any]], threshold: float = 0.85) -> list[dict[str, Any]]:
    seen_norms: list[str] = []
    result: list[dict[str, Any]] = []
    for item in items:
        norm = _normalize(item.get("title", ""))
        if not norm:
            continue
        if any(SequenceMatcher(None, norm, s).ratio() >= threshold for s in seen_norms):
            continue
        seen_norms.append(norm)
        result.append(item)
    return result

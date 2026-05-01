"""Text normalization helpers kept deterministic and dependency-free."""
from __future__ import annotations

import re
from collections.abc import Iterable

STOP_WORDS = set("""
a an and are as at be but by can could for from has have how i if in into is it its me my of on or our please should so the their them then there this to us we what when where who why will with you your
""".split())


def normalize(text: str | None) -> str:
    """Collapse whitespace without changing semantic content."""
    return re.sub(r"\s+", " ", (text or "").strip())


def tokenize(text: str) -> tuple[str, ...]:
    """Tokenize for BM25-style retrieval with a tiny deterministic stemmer."""
    words = re.findall(r"[a-zA-Z0-9$]+", (text or "").lower())
    out: list[str] = []
    for word in words:
        if word in STOP_WORDS or len(word) <= 1:
            continue
        for suffix in ("ing", "ed", "es", "s"):
            if len(word) > 5 and word.endswith(suffix):
                word = word[: -len(suffix)]
                break
        out.append(word)
    return tuple(out)


def has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(pattern in text for pattern in patterns)

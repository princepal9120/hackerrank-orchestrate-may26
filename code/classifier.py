"""Company classification helpers."""
from __future__ import annotations

from text_utils import normalize


def infer_company(issue: str, subject: str = "", company: str = "") -> str:
    explicit = normalize(company)
    if explicit and explicit.lower() != "none":
        return explicit
    text = f"{subject} {issue}".lower()
    if "visa" in text or "card" in text or "merchant" in text or "traveller" in text:
        return "Visa"
    if "claude" in text or "anthropic" in text or "bedrock" in text or "lti" in text:
        return "Claude"
    if any(term in text for term in ["hackerrank", "assessment", "candidate", "interview", "certificate"]):
        return "HackerRank"
    return "None"

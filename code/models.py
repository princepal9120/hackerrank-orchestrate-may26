"""Shared data models for the support triage pipeline."""
from __future__ import annotations

from dataclasses import dataclass

ALLOWED_STATUS = {"replied", "escalated"}
ALLOWED_REQUEST_TYPES = {"product_issue", "feature_request", "bug", "invalid"}


@dataclass(frozen=True)
class Ticket:
    issue: str
    subject: str = ""
    company: str = ""


@dataclass(frozen=True)
class Chunk:
    domain: str
    product_area: str
    path: str
    title: str
    text: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalHit:
    score: float
    chunk: Chunk


@dataclass(frozen=True)
class AgentResult:
    status: str
    product_area: str
    response: str
    justification: str
    request_type: str

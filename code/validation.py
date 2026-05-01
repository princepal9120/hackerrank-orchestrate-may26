"""Output schema validation and normalization."""
from __future__ import annotations

from models import ALLOWED_REQUEST_TYPES, ALLOWED_STATUS, AgentResult
from text_utils import normalize


def validate_result(result: AgentResult) -> AgentResult:
    status = result.status.lower().strip()
    request_type = result.request_type.lower().strip()
    if status not in ALLOWED_STATUS:
        status = "escalated"
    if request_type not in ALLOWED_REQUEST_TYPES:
        request_type = "product_issue"
    response = normalize(result.response) or "I don’t have enough support-corpus evidence to answer this safely, so I’m escalating it for human review."
    justification = normalize(result.justification) or "Decision is based on the provided support corpus and safety routing rules."
    return AgentResult(status, result.product_area.strip(), response, justification, request_type)

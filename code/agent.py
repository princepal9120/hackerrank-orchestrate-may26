"""Top-level support triage agent orchestration."""
from __future__ import annotations

import re

from classifier import infer_company
from models import AgentResult, Ticket
from paraphraser import paraphrase_if_enabled
from retrieval import BM25Retriever
from rules import SafetyRouter
from validation import validate_result


class SupportTriageAgent:
    def __init__(self, retriever: BM25Retriever, safety_router: SafetyRouter | None = None):
        self.retriever = retriever
        self.safety_router = safety_router or SafetyRouter()

    def triage(self, ticket: Ticket) -> AgentResult:
        routed = self.safety_router.route(ticket)
        if routed is not None:
            return validate_result(routed)

        inferred_company = infer_company(ticket.issue, ticket.subject, ticket.company)
        hits = self.retriever.search(f"{ticket.subject} {ticket.issue}", inferred_company, limit=3)
        if not hits or hits[0].score < 1.2:
            return validate_result(AgentResult("escalated", "", "I don’t have enough support-corpus evidence to answer this safely, so I’m escalating it for human review.", "Retrieval confidence was too low for a grounded response.", "invalid"))

        top = hits[0].chunk
        snippet = re.sub(r"\s+", " ", top.text).strip()[:550]
        response = f"Based on the relevant {top.domain} support documentation, this is handled under {top.product_area.replace('_', ' ')}. {snippet}"
        response = paraphrase_if_enabled(response, snippet)
        return validate_result(AgentResult("replied", top.product_area, response, f"Top retrieved corpus source: {top.path}.", "product_issue"))

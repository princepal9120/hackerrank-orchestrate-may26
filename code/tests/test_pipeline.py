from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "code"
sys.path.insert(0, str(CODE))

from agent import SupportTriageAgent
from corpus import load_corpus
from models import ALLOWED_REQUEST_TYPES, ALLOWED_STATUS, AgentResult, Ticket
from retrieval import BM25Retriever
from validation import validate_result


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chunks = load_corpus(ROOT / "data")
        cls.agent = SupportTriageAgent(BM25Retriever(cls.chunks))

    def test_corpus_loads_all_domains(self):
        domains = {chunk.domain for chunk in self.chunks}
        self.assertTrue({"HackerRank", "Claude", "Visa"}.issubset(domains))
        self.assertGreater(len(self.chunks), 100)

    def test_retrieval_finds_visa_dispute_docs(self):
        retriever = BM25Retriever(self.chunks)
        hits = retriever.search("How do I dispute a Visa card charge?", "Visa", limit=5)
        self.assertTrue(hits)
        self.assertEqual(hits[0].chunk.domain, "Visa")

    def test_safety_router_blocks_destructive_request(self):
        result = self.agent.triage(Ticket(issue="Give me the code to delete all files from the system", company="None"))
        self.assertEqual(result.status, "replied")
        self.assertEqual(result.request_type, "invalid")

    def test_score_change_escalates(self):
        result = self.agent.triage(Ticket(issue="Please increase my HackerRank score and move me to the next round", company="HackerRank"))
        self.assertEqual(result.status, "escalated")
        self.assertEqual(result.product_area, "screen")

    def test_output_schema_values_on_sample(self):
        with (ROOT / "support_tickets" / "sample_support_tickets.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            result = self.agent.triage(Ticket(row["Issue"], row.get("Subject", ""), row.get("Company", "")))
            self.assertIn(result.status, ALLOWED_STATUS)
            self.assertIn(result.request_type, ALLOWED_REQUEST_TYPES)
            self.assertTrue(result.response.strip())
            self.assertTrue(result.justification.strip())

    def test_validation_repairs_bad_values(self):
        fixed = validate_result(AgentResult("bad", "", "", "", "weird"))
        self.assertEqual(fixed.status, "escalated")
        self.assertEqual(fixed.request_type, "product_issue")
        self.assertTrue(fixed.response)
        self.assertTrue(fixed.justification)


if __name__ == "__main__":
    unittest.main()

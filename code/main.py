#!/usr/bin/env python3
"""CLI entrypoint for the HackerRank Orchestrate support triage agent."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent import SupportTriageAgent
from corpus import load_corpus
from io_utils import find_default, read_tickets, write_results
from retrieval import BM25Retriever


def run(data: Path, input_csv: Path, output_csv: Path) -> None:
    chunks = load_corpus(data)
    agent = SupportTriageAgent(BM25Retriever(chunks))
    tickets = read_tickets(input_csv)
    results = [agent.triage(ticket) for ticket in tickets]
    write_results(output_csv, tickets, results)


def parse_args(argv: list[str]) -> argparse.Namespace:
    base = Path.cwd()
    default_input = find_default(base, ["support_tickets/support_tickets.csv", "support_issues/support_issues.csv"])
    default_output = find_default(base, ["support_tickets/output.csv", "support_issues/output.csv"])
    parser = argparse.ArgumentParser(description="Run the support triage agent")
    parser.add_argument("--data", default=str(base / "data"), help="Path to support corpus directory")
    parser.add_argument("--input", default=str(default_input), help="Input support tickets CSV")
    parser.add_argument("--output", default=str(default_output), help="Output predictions CSV")
    parser.add_argument("--seed", default="42", help="Accepted for reproducibility; deterministic pipeline does not sample")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    run(Path(args.data), Path(args.input), Path(args.output))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

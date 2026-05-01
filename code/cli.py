#!/usr/bin/env python3
"""Product CLI for SupportRAG.

Commands:
  supportrag ingest  --url ... --output ...
  supportrag triage  --data ... --input ... --output ...
  supportrag eval    --data ... --sample ...
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from ingest_url import crawl
from main import run


def cmd_ingest(args: argparse.Namespace) -> int:
    written = crawl(args.url, Path(args.output), max_pages=args.max_pages, delay=args.delay)
    print(f"✅ Built corpus: {len(written)} pages -> {args.output}")
    print("Next: supportrag triage --data", args.output, "--input tickets.csv --output output.csv")
    return 0


def cmd_triage(args: argparse.Namespace) -> int:
    run(Path(args.data), Path(args.input), Path(args.output))
    print(f"✅ Wrote triage output: {args.output}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        pred_path = Path(td) / "predictions.csv"
        run(Path(args.data), Path(args.sample), pred_path)
        pred = list(csv.DictReader(pred_path.open(encoding="utf-8")))
    gold = list(csv.DictReader(open(args.sample, encoding="utf-8")))
    mapping = {"status": "Status", "product_area": "Product Area", "request_type": "Request Type"}
    print(f"Rows: {len(gold)}")
    for pred_col, gold_col in mapping.items():
        ok = sum(1 for p, g in zip(pred, gold) if (p[pred_col] or "").strip().lower() == (g[gold_col] or "").strip().lower())
        print(f"{pred_col}: {ok}/{len(gold)} = {ok/len(gold):.1%}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="supportrag",
        description="Build local support corpora and triage support tickets with deterministic RAG.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Crawl a public support URL into a local Markdown corpus")
    ingest.add_argument("--url", required=True, help="Starting support/help-center URL")
    ingest.add_argument("--output", required=True, help="Directory to write Markdown corpus into")
    ingest.add_argument("--max-pages", type=int, default=100)
    ingest.add_argument("--delay", type=float, default=0.2)
    ingest.set_defaults(func=cmd_ingest)

    triage = sub.add_parser("triage", help="Run support triage over an input CSV")
    triage.add_argument("--data", required=True, help="Local Markdown corpus directory")
    triage.add_argument("--input", required=True, help="Input CSV with Issue, Subject, Company columns")
    triage.add_argument("--output", required=True, help="Output CSV path")
    triage.set_defaults(func=cmd_triage)

    evaluate = sub.add_parser("eval", help="Evaluate against a labeled sample CSV")
    evaluate.add_argument("--data", required=True, help="Local Markdown corpus directory")
    evaluate.add_argument("--sample", required=True, help="Labeled sample CSV")
    evaluate.set_defaults(func=cmd_eval)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

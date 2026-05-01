# SupportRAG CLI

Turn any public support/help-center page into a local support-ticket triage agent.

SupportRAG is a deterministic CLI product for support teams, founders, and hackathon builders. It crawls support pages into a local Markdown corpus, retrieves relevant docs with BM25, applies safety/escalation rules, and outputs a clean support triage CSV.

## Why it is useful

Most support bots hallucinate. SupportRAG is designed for high-trust support workflows:

- Local corpus first. No unsupported web guessing.
- Deterministic BM25 retrieval.
- Rule-based escalation for risky cases.
- Optional LLM paraphrasing seam, disabled by default.
- CSV in, CSV out. Easy to plug into ops workflows.
- Works as a hackathon submission and a future product foundation.

## Install locally

```bash
git clone https://github.com/princepal9120/hackerrank-orchestrate-may26.git
cd hackerrank-orchestrate-may26
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

This installs two equivalent commands:

```bash
supportrag --help
supportbot --help

Without installation, use the repo-local launcher:

```bash
python3 supportrag.py --help
```
```

## Quickstart with any support page

### 1. Build a local corpus

```bash
python3 supportrag.py ingest \
  --url https://example.com/support \
  --output corpora/example-support \
  --max-pages 100
```

### 2. Create tickets CSV

```csv
Issue,Subject,Company
"How can I reset billing?","Billing help","ExampleCo"
"The whole product is down","Urgent","ExampleCo"
```

### 3. Triage tickets

```bash
python3 supportrag.py triage \
  --data corpora/example-support \
  --input tickets.csv \
  --output output.csv
```

Output columns:

```csv
issue,subject,company,response,product_area,status,request_type,justification
```

Allowed values:

- `status`: `replied`, `escalated`
- `request_type`: `product_issue`, `feature_request`, `bug`, `invalid`

## HackerRank Orchestrate submission mode

The original challenge entrypoint still works:

```bash
python3 code/main.py \
  --data data \
  --input support_tickets/support_tickets.csv \
  --output support_tickets/output.csv
```

## Product architecture

```txt
URL support page
  -> ingest_url.py
  -> local Markdown corpus
  -> corpus.py chunking
  -> retrieval.py BM25
  -> rules.py safety router
  -> agent.py orchestration
  -> validation.py schema guard
  -> output.csv
```

## What makes this product-ready

- Installable Python package via `pyproject.toml`.
- Real CLI commands: `ingest`, `triage`, `eval`.
- No required third-party dependencies.
- Local-first support corpus design.
- Clear upgrade path to SaaS:
  - corpus registry
  - incremental recrawls
  - embedding reranker
  - tenant-specific safety policies
  - dashboard/API
  - citations and confidence scores

## Current limitations

- The crawler is a deterministic stdlib HTML crawler, not a browser. JavaScript-heavy docs may need a future Playwright ingestion backend.
- Safety rules are currently tuned for the HackerRank/Claude/Visa challenge and should become configurable policies for production customers.
- Optional LLM paraphrasing is intentionally disabled by default for reproducibility.

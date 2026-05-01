# SupportRAG CLI

**A local-first support triage CLI that turns any public support page into a ticket-answering agent.**

SupportRAG crawls support docs, builds a local Markdown corpus, retrieves answers with deterministic BM25, applies safety and escalation rules, then outputs a clean CSV for support workflows.

PyPI: <https://pypi.org/project/supportrag-cli/>

```bash
pip install supportrag-cli
```

```bash
supportrag --help
```

## What it does

- Crawls a public support/help-center URL into a local corpus.
- Runs deterministic BM25 retrieval over the corpus.
- Classifies tickets into reply vs escalation.
- Avoids unsupported claims by escalating risky or low-evidence cases.
- Produces CSV output with response, status, product area, request type, and justification.
- Works as both a product CLI and a HackerRank Orchestrate hackathon submission.

## Quickstart

### 1. Install

```bash
pip install supportrag-cli
```

### 2. Ingest a support site

```bash
supportrag ingest \
  --url https://example.com/support \
  --output corpora/example-support \
  --max-pages 100
```

### 3. Create tickets CSV

```csv
Issue,Subject,Company
"How do I reset my password?","Password help","ExampleCo"
"The whole product is down","Urgent outage","ExampleCo"
```

Save it as `tickets.csv`.

### 4. Triage tickets

```bash
supportrag triage \
  --data corpora/example-support \
  --input tickets.csv \
  --output output.csv
```

### 5. View output

```bash
cat output.csv
```

Output columns:

```txt
issue, subject, company, response, product_area, status, request_type, justification
```

Allowed values:

- `status`: `replied`, `escalated`
- `request_type`: `product_issue`, `feature_request`, `bug`, `invalid`

## Example with this repo

```bash
git clone https://github.com/princepal9120/hackerrank-orchestrate-may26.git
cd hackerrank-orchestrate-may26

pip install supportrag-cli

supportrag triage \
  --data data \
  --input examples/tickets.csv \
  --output examples/output.csv
```

## Architecture

```txt
Support URL
  -> ingest_url.py
  -> local Markdown corpus
  -> corpus.py chunking and metadata
  -> retrieval.py BM25 retrieval
  -> rules.py safety and escalation router
  -> agent.py orchestration
  -> validation.py schema guard
  -> output.csv
```

## Why this approach

Support workflows need trust more than flashy agent loops. SupportRAG uses:

- **Local corpus grounding:** answers come from ingested docs.
- **Deterministic retrieval:** reproducible BM25 scoring.
- **Explicit safety rules:** billing, account access, assessment results, security, outages, and vague tickets are handled conservatively.
- **Schema validation:** every output row is normalized before writing.
- **Optional LLM seam:** paraphrasing can be added later, after retrieval and validation, without changing routing decisions.

## Commands

```bash
supportrag ingest --help
supportrag triage --help
supportrag eval --help
```

Aliases:

```bash
supportbot --help
```

Repo-local launcher if you do not install the package:

```bash
python3 supportrag.py --help
```

## Product roadmap

- Corpus registry: `supportbot corpus add <name> <url>`.
- Incremental recrawls and page hashing.
- Configurable tenant-specific safety policies.
- Optional embedding reranker after BM25.
- Optional LLM paraphrasing after validation.
- API server and dashboard.
- Source citations and confidence scores.
- Regression eval sets per customer.

## HackerRank Orchestrate submission

This repository was originally built for the **HackerRank Orchestrate** 24-hour hackathon, May 1 to 2, 2026.

Challenge: build a terminal-based support triage agent across three ecosystems:

- HackerRank Support
- Claude Help Center
- Visa Support

The hackathon path remains intact and uses only the provided local corpus.

Run final predictions:

```bash
python3 code/main.py \
  --data data \
  --input support_tickets/support_tickets.csv \
  --output support_tickets/output.csv
```

Evaluate on sample labels:

```bash
python3 code/evaluate.py \
  --data data \
  --sample support_tickets/sample_support_tickets.csv
```

Submission files:

1. `submission_code.zip`
2. `support_tickets/output.csv`
3. `$HOME/hackerrank_orchestrate/log.txt`

## Repository layout

```txt
.
├── code/
│   ├── cli.py              # Product CLI commands
│   ├── ingest_url.py       # URL to local Markdown corpus
│   ├── main.py             # Hackathon-compatible entrypoint
│   ├── agent.py            # Triage orchestration
│   ├── retrieval.py        # BM25 retriever
│   ├── rules.py            # Safety and escalation rules
│   ├── validation.py       # Output schema guard
│   └── tests/              # Regression tests
├── data/                   # Provided hackathon corpus
├── examples/               # Product CLI examples
├── support_tickets/        # Hackathon input/output CSVs
├── PRODUCT_README.md       # Product-focused docs
├── pyproject.toml          # PyPI packaging
└── supportrag.py           # Repo-local CLI launcher
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python3 -m unittest discover -s code/tests -p 'test_*.py' -v
```

Build package:

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```

## Links

- PyPI: <https://pypi.org/project/supportrag-cli/>
- Repository: <https://github.com/princepal9120/hackerrank-orchestrate-may26>
- Product docs: [`PRODUCT_README.md`](./PRODUCT_README.md)

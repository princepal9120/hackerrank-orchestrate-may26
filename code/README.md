# SupportRAG CLI / HackerRank Orchestrate Agent

This `code/` directory contains the full support triage engine used for the HackerRank Orchestrate submission and the reusable **SupportRAG CLI** product.

SupportRAG is a local-first support triage agent. It loads support docs, retrieves relevant evidence with deterministic BM25, applies explicit safety and escalation rules, validates structured output, and writes ticket responses to CSV.

PyPI package:

<https://pypi.org/project/supportrag-cli/>

## Install SupportRAG CLI

```bash
pip install supportrag-cli
```

Check install:

```bash
supportrag --help
```

Alias:

```bash
supportbot --help
```

## SupportRAG CLI use case

Use SupportRAG when you want to turn a support/help-center page into a reusable ticket triage agent.

Example workflow:

1. Crawl a public support site into a local corpus.
2. Prepare a CSV of support tickets.
3. Run deterministic triage.
4. Get an output CSV with reply/escalation status, product area, response, request type, and justification.

### 1. Ingest support documentation

```bash
supportrag ingest \
  --url https://example.com/support \
  --output corpora/example-support \
  --max-pages 100
```

### 2. Create tickets CSV

```csv
Issue,Subject,Company
"How do I reset my password?","Password help","ExampleCo"
"The product is down for everyone","Urgent outage","ExampleCo"
```

### 3. Run triage

```bash
supportrag triage \
  --data corpora/example-support \
  --input tickets.csv \
  --output output.csv
```

### 4. Output format

```csv
issue,subject,company,response,product_area,status,request_type,justification
```

Allowed values:

- `status`: `replied`, `escalated`
- `request_type`: `product_issue`, `feature_request`, `bug`, `invalid`

## Hackathon submission mode

The HackerRank challenge entrypoint is still `code/main.py`.

From the repository root:

```bash
python3 code/main.py \
  --data data \
  --input support_tickets/support_tickets.csv \
  --output support_tickets/output.csv \
  --seed 42
```

This mode uses only the provided local `data/` corpus and writes the required prediction file.

## Evaluate on sample labels

```bash
python3 code/evaluate.py \
  --data data \
  --sample support_tickets/sample_support_tickets.csv
```

## Tests

No third-party dependency is required for the deterministic path.

```bash
python3 -m unittest discover -s code/tests -p 'test_*.py' -v
```

## Architecture

```txt
cli.py           Product CLI: ingest, triage, eval
main.py          Hackathon-compatible CLI entrypoint
ingest_url.py    Public support URL -> local Markdown corpus
io_utils.py      CSV input/output and default path detection
models.py        Ticket, Chunk, RetrievalHit, AgentResult models
text_utils.py    Normalization and tokenization
corpus.py        Markdown corpus loading, metadata extraction, chunking
retrieval.py     Dependency-free BM25-style retriever
classifier.py    Company inference
rules.py         Explicit safety and escalation router
agent.py         Orchestration: rules first, retrieval fallback second
validation.py    Schema/value normalization
paraphraser.py   Optional LLM paraphrase seam, disabled by default
evaluate.py      Sample-label evaluation helper
tests/           Regression tests
```

## Why this design

The rubric rewards grounded answers, reproducibility, and safe escalation. The primary path is:

1. Load a local corpus.
2. Build bounded Markdown chunks with domain and product-area metadata.
3. Run deterministic BM25-style retrieval.
4. Apply explicit rule-based safety before generic retrieval answers.
5. Validate every output row against allowed schema values.
6. Escalate instead of guessing when evidence is weak or the action is sensitive.

The optional LLM paraphraser is isolated in `paraphraser.py` and disabled by default. It cannot change status, request type, product area, routing, or evidence. This keeps the submitted behavior reproducible.

## Product roadmap

- Add corpus registry commands.
- Add incremental recrawls and page hashing.
- Add configurable safety policies per company.
- Add optional embedding reranker after BM25.
- Add optional LLM paraphrasing after validation.
- Add API server and dashboard.
- Add source citations and confidence scores.

## Judge interview notes

Key tradeoff: I chose deterministic BM25 plus explicit safety rules over an opaque agent loop because support triage punishes hallucination. The system answers only when it has a safe product pattern or corpus evidence. It escalates account mutation, billing/order details, assessment outcomes, broad service failures, unsupported privacy specifics, and vague tickets.

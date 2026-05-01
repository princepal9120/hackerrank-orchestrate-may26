# Future Product Workflow

This repo now has two modes.

## 1. Hackathon mode

Use only the provided corpus:

```bash
python3 code/main.py \
  --data data \
  --input support_tickets/support_tickets.csv \
  --output support_tickets/output.csv
```

This is the submission-safe path.

## 2. Product mode

Use the same support triage engine on another public support page.

### Step A: build a local corpus from a support URL

```bash
python3 code/ingest_url.py \
  --url https://example.com/support \
  --output corpora/example-support \
  --max-pages 100
```

The ingester crawls same-domain HTML pages, extracts readable text, and stores local Markdown files.

### Step B: run triage against that corpus

Prepare a CSV with columns:

```csv
Issue,Subject,Company
"How do I reset billing?","Billing help","ExampleCo"
```

Then run:

```bash
python3 code/main.py \
  --data corpora/example-support \
  --input tickets.csv \
  --output output.csv
```

## Product architecture direction

To turn this into a real product later:

- Add a persisted corpus registry: `supportbot corpus add <name> <url>`.
- Store crawl metadata: source URL, crawl time, page hash, title, status.
- Add incremental refresh: only re-index changed pages.
- Add tenant-specific safety policies: billing, account access, refunds, legal, security.
- Add optional embeddings as a reranker, not as the only retriever.
- Add optional LLM paraphrasing after deterministic routing and validation.
- Add citations in UI/API responses from `Chunk.path` and source URLs.
- Add eval sets per customer to avoid regressions.

Important: product mode should still answer only from the locally ingested corpus. The URL is for building the corpus, not for live unsupported guessing.

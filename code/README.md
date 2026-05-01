# HackerRank Orchestrate Support Triage Agent

Terminal-based support triage agent for the HackerRank Orchestrate challenge.

## Architecture

The solution is intentionally boring in the best way: deterministic, explainable, and safe.

```txt
main.py          CLI entrypoint
io_utils.py      CSV input/output and default path detection
models.py        Ticket, Chunk, RetrievalHit, AgentResult models
text_utils.py    normalization and tokenization
corpus.py        Markdown corpus loading, metadata extraction, chunking
retrieval.py     dependency-free BM25-style retriever
classifier.py    company inference
rules.py         explicit safety and escalation router
agent.py         orchestration: rules first, retrieval fallback second
validation.py    schema/value normalization
paraphraser.py   optional LLM paraphrase seam, disabled by default
evaluate.py      sample-label evaluation helper
tests/           lightweight regression tests
```

## Why this design

The rubric rewards grounded answers, reproducibility, and safe escalation. So the primary path is:

1. Load only the provided `data/` corpus.
2. Build bounded Markdown chunks with domain and product-area metadata.
3. Run deterministic BM25-style retrieval.
4. Apply explicit rule-based safety before generic retrieval answers.
5. Validate every output row against allowed schema values.
6. Escalate instead of guessing when evidence is weak or the action is sensitive.

The optional LLM paraphraser is isolated in `paraphraser.py` and disabled by default. It cannot change status, request type, product area, routing, or evidence. This keeps the submitted behavior reproducible.

## Run final predictions

From the repository root:

```bash
python3 code/main.py \
  --data data \
  --input support_tickets/support_tickets.csv \
  --output support_tickets/output.csv \
  --seed 42
```

The CLI also supports the alternate `support_issues/` naming from the public README.

## Evaluate on sample labels

```bash
python3 code/evaluate.py \
  --data data \
  --sample support_tickets/sample_support_tickets.csv
```

## Tests

No third-party dependency is required. Run:

```bash
python3 -m unittest discover -s code/tests -p 'test_*.py'
```

## Dependencies

Python 3 standard library only.


## Future product mode

This submission also includes an optional URL-to-local-corpus ingester for future product use. It is separate from the hackathon prediction path.

```bash
python3 code/ingest_url.py \
  --url https://example.com/support \
  --output corpora/example-support \
  --max-pages 100

python3 code/main.py \
  --data corpora/example-support \
  --input tickets.csv \
  --output output.csv
```

See `code/product_workflow.md` for the full productization path.

## Judge interview notes

Key tradeoff: I chose deterministic BM25 plus explicit safety rules over an opaque agent loop because support triage punishes hallucination. The system answers only when it has a safe product pattern or corpus evidence. It escalates account mutation, billing/order details, assessment outcomes, broad service failures, unsupported privacy specifics, and vague tickets.

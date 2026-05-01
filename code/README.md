# HackerRank Orchestrate Support Triage Agent

This is a terminal-based support triage agent for the HackerRank Orchestrate challenge.

## Approach

The agent uses a deterministic, corpus-first pipeline:

1. Load all Markdown support articles from `data/`.
2. Split articles into retrieval chunks with company, product area, title, and path metadata.
3. Use local BM25-style retrieval to ground each ticket in the provided corpus.
4. Apply explicit safety and escalation rules for risky cases such as billing, account access, assessment outcomes, broad outages, refunds, and unsupported requests.
5. Produce a schema-valid CSV with lowercase allowed values.

The design intentionally avoids making unsupported claims. If the corpus or routing rules do not support a safe answer, the ticket is escalated.

## Run

From the repository root:

```bash
python3 code/main.py \
  --data data \
  --input support_tickets/support_tickets.csv \
  --output support_tickets/output.csv \
  --seed 42
```

The code also supports the alternate `support_issues/` naming used in the public README.

## Evaluate on sample labels

```bash
python3 code/evaluate.py \
  --data data \
  --sample support_tickets/sample_support_tickets.csv
```

## Dependencies

No third-party package is required for the deterministic path. The implementation uses Python 3 standard library only.

## Engineering notes

- Secrets are not hardcoded or required.
- Output values are validated against the allowed status and request type sets.
- The response generator is conservative and does not expose internal reasoning or retrieved raw documents.
- The implementation favors reproducibility and judge explainability over opaque agent loops.

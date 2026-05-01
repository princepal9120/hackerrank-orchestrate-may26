# Examples

Run the product CLI on the included challenge corpus:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python3 supportrag.py triage \
  --data data \
  --input examples/tickets.csv \
  --output examples/output.csv
```

Build a corpus from a public support site:

```bash
python3 supportrag.py ingest \
  --url https://example.com/support \
  --output corpora/example-support \
  --max-pages 100
```

"""CSV IO utilities and command defaults."""
from __future__ import annotations

import csv
from pathlib import Path

from models import AgentResult, Ticket

FIELDNAMES = ["issue", "subject", "company", "response", "product_area", "status", "request_type", "justification"]


def find_default(base: Path, names: list[str]) -> Path:
    for name in names:
        path = base / name
        if path.exists():
            return path
    return base / names[0]


def read_tickets(input_csv: Path) -> list[Ticket]:
    with input_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [Ticket(row.get("Issue") or row.get("issue") or "", row.get("Subject") or row.get("subject") or "", row.get("Company") or row.get("company") or "") for row in rows]


def write_results(output_csv: Path, tickets: list[Ticket], results: list[AgentResult]) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for ticket, result in zip(tickets, results):
            writer.writerow({"issue": ticket.issue, "subject": ticket.subject, "company": ticket.company, "response": result.response, "product_area": result.product_area, "status": result.status, "request_type": result.request_type, "justification": result.justification})

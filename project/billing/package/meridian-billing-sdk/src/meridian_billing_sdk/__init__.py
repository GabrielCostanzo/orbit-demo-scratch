"""Read and validate the demo's invoice format."""

import json
from pathlib import Path

NAME = "meridian-billing-sdk"


def read_invoices(path: str | Path) -> list[dict]:
    invoices = json.loads(Path(path).read_text())
    if not isinstance(invoices, list) or not invoices:
        raise ValueError("Provide a nonempty JSON list of invoices.")
    seen = set()
    for invoice in invoices:
        if not isinstance(invoice, dict):
            raise ValueError("Each invoice must be an object.")
        for field in ("id", "customer"):
            if not isinstance(invoice.get(field), str) or not invoice[field].strip():
                raise ValueError(f"Each invoice needs a {field}.")
        for field in ("quantity", "unit_price_cents"):
            if type(invoice.get(field)) is not int or invoice[field] <= 0:
                raise ValueError(f"{field} must be a positive integer.")
        if invoice["id"] in seen:
            raise ValueError(f"Duplicate invoice: {invoice['id']}")
        seen.add(invoice["id"])
    return invoices


def total_cents(invoices: list[dict]) -> int:
    return sum(row["quantity"] * row["unit_price_cents"] for row in invoices)


def summary(invoices: list[dict]) -> str:
    cents = total_cents(invoices)
    return f"{len(invoices)} invoices · total ${cents // 100}.{cents % 100:02d}"

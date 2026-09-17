"""Generate balanced entries from validated invoices."""

from meridian_billing_models import Entry

NAME = "meridian-billing-ledger"


def post_invoices(invoices: list[dict]) -> list[Entry]:
    entries = []
    for invoice in invoices:
        cents = invoice["quantity"] * invoice["unit_price_cents"]
        entries.extend([
            Entry(invoice["id"], "receivables", debit_cents=cents),
            Entry(invoice["id"], "revenue", credit_cents=cents),
        ])
    return entries

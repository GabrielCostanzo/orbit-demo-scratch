"""Ledger entries used by the protected billing bundle."""

from dataclasses import dataclass

NAME = "meridian-billing-models"


@dataclass(frozen=True)
class Entry:
    invoice_id: str
    account: str
    debit_cents: int = 0
    credit_cents: int = 0

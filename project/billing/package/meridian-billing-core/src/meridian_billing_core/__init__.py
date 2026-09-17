"""Process invoices with the protected ledger bundle."""

from meridian_billing_ledger import post_invoices
from meridian_billing_sdk import read_invoices

NAME = "meridian-billing-core"


def process(path):
    invoices = read_invoices(path)
    return invoices, post_invoices(invoices)

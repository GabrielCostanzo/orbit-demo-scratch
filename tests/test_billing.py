"""Exercise installed packages, including the optional release chapter's change."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from meridian_billing_core import process
from meridian_billing_sdk import read_invoices, summary, total_cents

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/invoices.json"


class BillingTests(unittest.TestCase):
    def test_invoice_total_and_balanced_entries(self):
        invoices, entries = process(EXAMPLE)
        self.assertEqual(summary(invoices), "3 invoices · total $48.00")
        self.assertEqual(total_cents(invoices), 4800)
        self.assertEqual(len(entries), 6)
        for invoice in invoices:
            pair = [entry for entry in entries if entry.invoice_id == invoice["id"]]
            self.assertEqual([entry.account for entry in pair], ["receivables", "revenue"])
            self.assertEqual(sum(entry.debit_cents for entry in pair),
                             invoice["quantity"] * invoice["unit_price_cents"])
            self.assertEqual(sum(entry.credit_cents for entry in pair),
                             invoice["quantity"] * invoice["unit_price_cents"])

    def test_rejects_invalid_invoice_batches(self):
        valid = {"id": "A", "customer": "Northstar", "quantity": 1, "unit_price_cents": 25}
        invalid = [{}, [], [valid, valid], [{**valid, "customer": ""}],
                   [{**valid, "quantity": True}], [{**valid, "unit_price_cents": 1.5}],
                   [{**valid, "quantity": 0}], [{**valid, "unit_price_cents": -1}]]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "invoices.json"
            for value in invalid:
                with self.subTest(value=value):
                    path.write_text(json.dumps(value))
                    with self.assertRaises(ValueError):
                        read_invoices(path)

    def test_command_reports_input_failure_without_traceback(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "broken.json"
            path.write_text("not json")
            result = subprocess.run([sys.executable, "-m", "meridian_billing_sdk", str(path)],
                                    capture_output=True, text=True, cwd=temp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("meridian-invoices:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_customer_filter_after_release_exercise(self):
        help_result = subprocess.run([sys.executable, "-m", "meridian_billing_sdk", "--help"],
                                     capture_output=True, text=True, check=True)
        if "--customer" not in help_result.stdout:
            self.skipTest("The customer filter is added in chapter 4.")
        for customer, expected in [("Northstar", "2 invoices · total $28.00"),
                                   ("Unknown", "0 invoices · total $0.00")]:
            with self.subTest(customer=customer):
                result = subprocess.run([sys.executable, "-m", "meridian_billing_sdk", str(EXAMPLE),
                                         "--customer", customer], capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout.strip(), expected)

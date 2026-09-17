"""The billing Application uses the same installed wheels as package consumers."""

import importlib.util
import json
from pathlib import Path
import threading
import unittest
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("billing_server", ROOT / "project/billing/application/billing-api/server.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class BillingAPITests(unittest.TestCase):
    def test_running_api_returns_health_invoice_totals_and_not_found(self):
        with app.server(("127.0.0.1", 0), ROOT / "examples/invoices.json") as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                with urllib.request.urlopen(base + "/health", timeout=2) as response:
                    self.assertEqual(json.load(response), {"status": "ready", "application": "billing-api"})
                with urllib.request.urlopen(base + "/invoices", timeout=2) as response:
                    self.assertEqual(json.load(response), {"invoices": 3, "total_cents": 4800, "ledger_entries": 6})
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(base + "/missing", timeout=2)
                self.assertEqual(raised.exception.code, 404)
            finally:
                server.shutdown()
                worker.join(timeout=3)

"""Serve Meridian's sample invoices using the installed billing packages."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

from meridian_billing_core import process
from meridian_billing_sdk import total_cents

EXAMPLE = Path(__file__).resolve().parent / "examples/invoices.json"


class BillingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status, body = 200, {"status": "ready", "application": "billing-api"}
        elif self.path == "/invoices":
            invoices, entries = process(self.server.invoice_path)
            status, body = 200, {"invoices": len(invoices), "total_cents": total_cents(invoices),
                                 "ledger_entries": len(entries)}
        else:
            status, body = 404, {"error": "not_found"}
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def server(address=("0.0.0.0", 8080), invoice_path=EXAMPLE):
    instance = ThreadingHTTPServer(address, BillingHandler)
    instance.invoice_path = invoice_path
    return instance


if __name__ == "__main__":
    with server() as instance:
        instance.serve_forever()

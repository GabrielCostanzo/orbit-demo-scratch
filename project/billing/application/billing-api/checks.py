"""Post-build checks executed inside the image; exit status is the real result."""

import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request


def smoke():
    for attempt in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=1) as response:
                health = json.load(response)
            break
        except (OSError, urllib.error.URLError):
            if attempt == 29:
                raise
            time.sleep(0.2)
    if health != {"status": "ready", "application": "billing-api"}:
        raise ValueError("Unexpected health response")
    with urllib.request.urlopen("http://127.0.0.1:8080/invoices", timeout=2) as response:
        invoices = json.load(response)
    if invoices != {"invoices": 3, "total_cents": 4800, "ledger_entries": 6}:
        raise ValueError("The running image returned incorrect invoice totals")
    inputs = json.loads(Path("/app/build-inputs.json").read_text())
    for package, record in inputs["packages"].items():
        if importlib.metadata.version(package) != record["version"]:
            raise ValueError(f"Installed version differs from the tested wheel: {package}")
    print("Smoke passed: running API, 3 invoices, $48.00, 6 ledger entries; installed versions match inputs.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=["smoke", "regression"])
    args = parser.parse_args()
    if args.check == "regression":
        return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "/app/tests",
                               "-p", "test_billing.py", "-v"], check=False).returncode
    smoke()
    return 0


if __name__ == "__main__":
    sys.exit(main())

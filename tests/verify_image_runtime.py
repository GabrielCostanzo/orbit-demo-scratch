"""Run on a Docker runner. Local image proof; does not contact Orbit or a CI API."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
FILES = ["Dockerfile", ".dockerignore", "examples/invoices.json", "tests/test_billing.py",
         "project/billing/application/billing-api/server.py",
         "project/billing/application/billing-api/checks.py"]


def run(*args, capture=False, **kwargs):
    result = subprocess.run([str(arg) for arg in args], check=True, text=True,
                            stdout=subprocess.PIPE if capture else None, **kwargs)
    return (result.stdout or "").strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    nonce = uuid.uuid4().hex[:12]
    registry_id = image_tag = None
    image_built = False
    try:
        with tempfile.TemporaryDirectory(prefix="meridian-image-proof-") as temporary:
            folder = Path(temporary)
            artifacts = folder / "distributions"
            run(ROOT / "demo", "build", "--out", artifacts, cwd=ROOT)
            context = folder / "context"
            run(ROOT / "demo", "image-context", "--artifacts", artifacts,
                "--out", context / ".orbit-image-context", cwd=ROOT)
            for name in FILES:
                destination = context / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)

            # A private disposable registry gives this test a real pullable digest.
            # No tenant, hosted CI run, or Orbit validation evidence is created.
            registry_id = run("docker", "run", "--detach", "--name", "meridian-image-proof-" + nonce,
                              "--memory", "384m", "--cpus", "1", "--pids-limit", "64",
                              "--tmpfs", "/var/lib/registry:size=256m", "--publish", "127.0.0.1::5000",
                              "registry:2", capture=True)
            binding = run("docker", "port", registry_id, "5000/tcp", capture=True)
            port = binding.rsplit(":", 1)[1]
            for attempt in range(30):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/v2/", timeout=2):
                        break
                except OSError:
                    if attempt == 29:
                        raise
                    time.sleep(0.2)
            image_tag = f"localhost:{port}/meridian-billing:{nonce}"
            run("docker", "build", "--tag", image_tag, context)
            image_built = True
            run("docker", "push", image_tag)
            references = json.loads(run("docker", "image", "inspect", image_tag,
                                        "--format", "{{json .RepoDigests}}", capture=True))
            prefix = f"localhost:{port}/meridian-billing@sha256:"
            reference = next(value for value in references if value.startswith(prefix))
            for key in ["smoke", "regression"]:
                definition = {"workflow": "meridian/billing-" + key, "version": "1", "parameters": {}}
                digest = hashlib.sha256(json.dumps(definition, sort_keys=True,
                                                   separators=(",", ":")).encode()).hexdigest()
                run("env", "ORBIT_IMAGE=" + reference, "ORBIT_VALIDATION_KEY=" + key,
                    "ORBIT_VALIDATION_DEFINITION_SHA256=" + digest,
                    "sh", ROOT / "scripts/meridian-validation.sh")
            report = {
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "scope": "Real wheel build, unit tests, Docker build/push, immutable image smoke and regression",
                "orbit_or_hosted_ci_executed": False,
                "image_digest": reference.rsplit("@", 1)[1],
                "checks": {"smoke": "passed", "regression": "passed"},
                "source_sha256": {
                    name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                    for name in FILES + ["scripts/demo.py", "scripts/meridian-validation.sh"]
                },
            }
    finally:
        try:
            if image_built:
                # The tag belongs to this run's ephemeral registry and random nonce.
                run("docker", "image", "rm", image_tag)
        finally:
            if registry_id:
                run("docker", "rm", "--force", "--volumes", registry_id)
    report["created_containers_removed"] = True
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

"""Shortcuts for the documented Orbit demo; credentials stay in registry's keyring."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ORBIT_REF = "cbc8e19965cf03fe491e70287e5375c72f2ee7db"
ORBIT_ORIGIN = "https://orbit-staging.home.costanga.com"
PACKAGES = {
    "meridian-billing-sdk": "project/billing/package/meridian-billing-sdk",
    "meridian-auth": "package/library/auth/meridian-auth",
    "meridian-billing-models": "project/billing/package/meridian-billing-models",
    "meridian-billing-ledger": "project/billing/package/meridian-billing-ledger",
    "meridian-billing-core": "project/billing/package/meridian-billing-core",
}
ARTIFACT_NAME = "meridian-distributions"


def run(*args: object, capture: bool = False, cwd: Path = ROOT) -> str:
    command = [str(arg) for arg in args]
    if not capture:
        print("+ " + shlex.join(command), flush=True)
    result = subprocess.run(command, cwd=cwd, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return (result.stdout or "").strip()


def state_dir() -> Path:
    checkout = hashlib.sha256(str(ROOT).encode()).hexdigest()[:16]
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    path = base / "orbit-demo" / checkout
    path.mkdir(parents=True, exist_ok=True)
    return path


def version(package: str) -> str:
    return tomllib.loads((ROOT / PACKAGES[package] / "pyproject.toml").read_text())["project"]["version"]


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def context() -> dict:
    return json.loads(run("registry", "context", "show", "--json", capture=True))


def server_commit(origin: str) -> str | None:
    """Best-effort: the Orbit revision an origin reports; never raises."""
    try:
        with urllib.request.urlopen(f"{origin}/+version", timeout=5) as response:
            commit = json.loads(response.read())["commit"]
        return commit if isinstance(commit, str) else None
    except Exception:
        return None


def setup(source: Path | None) -> None:
    if source is None:
        source = state_dir() / "orbit-source"
        if not (source / ".git").exists():
            source.mkdir(exist_ok=True)
            run("git", "init", source)
        try:
            run("git", "-C", source, "fetch", "--depth=1",
                "https://github.com/GabrielCostanzo/orbit.git", ORBIT_REF)
        except subprocess.CalledProcessError:
            raise ValueError("The tested Orbit revision is not available remotely. "
                             "Use ./demo setup --source /path/to/orbit with that revision.") from None
        run("git", "-C", source, "checkout", "--detach", ORBIT_REF)
    package = source.expanduser().resolve() / "project/python-package-registry/package/registry-cli"
    if not (package / "pyproject.toml").is_file():
        raise ValueError("--source must point to the Orbit repository, not orbit-demo.")
    run("uv", "tool", "install", "--force", "--reinstall", "--with-executables-from", "keyring",
        "--default-index", "https://pypi.org/simple", package)
    run("uv", "tool", "install", "--force", "--default-index", "https://pypi.org/simple",
        "launchpad-uv==0.1.1")
    run("registry", "--version")
    write_json(state_dir() / "orbit-source.json", {"path": str(source.expanduser().resolve())})
    commit = server_commit(ORBIT_ORIGIN)
    if commit and commit != ORBIT_REF:
        print(f"warning: the installed Orbit CLI is pinned to {ORBIT_REF[:12]} but {ORBIT_ORIGIN} runs "
              f"{commit[:12]}; bump ORBIT_REF in scripts/demo.py or use "
              f"./demo setup --source <path-to-orbit-at-that-commit>", file=sys.stderr)
    print("Ready. Next: tutorial/00-orientation.md (Create your registry).")


def build(output: Path) -> None:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Build output must be empty; choose a new --out directory.")
    wheels = []
    artifacts = {}
    for package in PACKAGES:
        dest = output / package
        run("uv", "build", "--package", package, "--out-dir", dest,
            "--no-create-gitignore", "--default-index", "https://pypi.org/simple")
        files = sorted(dest.iterdir())
        if (len(files) != 2 or sum(p.suffix == ".whl" for p in files) != 1
                or not any(p.name.endswith(".tar.gz") for p in files)):
            raise ValueError(f"Expected one wheel and one sdist for {package}.")
        wheels.extend(p for p in files if p.suffix == ".whl")
        artifacts[package] = {
            "version": version(package),
            "files": [{"filename": p.name, "size": p.stat().st_size,
                       "sha256_digest": digest(p)} for p in files],
        }
    with tempfile.TemporaryDirectory(prefix="meridian-wheel-test-") as temp:
        folder = Path(temp)
        run("uv", "venv", folder / ".venv", "--python", "3.12", cwd=folder)
        python = folder / ".venv/bin/python"
        run("uv", "pip", "install", "--python", python, "--no-index", *wheels, cwd=folder)
        run(python, "-m", "unittest", "discover", "-s", ROOT / "tests", cwd=folder)
        run(folder / ".venv/bin/meridian-invoices", ROOT / "examples/invoices.json", cwd=folder)
        run(folder / ".venv/bin/meridian-billing", ROOT / "examples/invoices.json", cwd=folder)
    revision = run("git", "rev-parse", "HEAD", capture=True)
    if os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_SHA") != revision:
        raise ValueError("CI checkout does not match GITHUB_SHA.")
    write_json(output / "manifest.json", {
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "revision": revision, "packages": artifacts,
    })
    print(f"Built and tested all five distributions. Artifacts: {output}")


def github_repository(remote: str) -> str:
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([\w.-]+/[\w.-]+?)(?:\.git)?", remote)
    if not match:
        raise ValueError("origin must be your GitHub fork (HTTPS or SSH).")
    return match[1]


def verify_run(result: dict, repository: str, revision: str) -> None:
    if (result.get("status") != "completed" or result.get("conclusion") != "success"
            or result.get("headSha") != revision or result.get("event") not in {"push", "workflow_dispatch"}
            or result.get("workflowName") != "Build and test distributions"
            or result.get("url") != f"https://github.com/{repository}/actions/runs/{result.get('databaseId')}"):
        raise ValueError("Choose a successful Build and test distributions run on this exact commit in your fork.")


def verify_manifest(manifest: dict, result: dict, repository: str, directory: Path) -> None:
    if (manifest.get("repository") != repository or manifest.get("revision") != result["headSha"]
            or manifest.get("run_id") != str(result["databaseId"])
            or manifest.get("run_attempt") != str(result["attempt"])):
        raise ValueError("CI artifacts do not belong to the selected repository, revision, and run attempt.")
    verify_distribution_files(manifest, directory)


def verify_distribution_files(manifest: dict, directory: Path) -> None:
    if set(manifest.get("packages", {})) != set(PACKAGES):
        raise ValueError("CI artifacts must include every demo package.")
    for package, record in manifest["packages"].items():
        files = record["files"]
        if record["version"] != version(package) or len(files) != 2:
            raise ValueError(f"CI package/version mismatch: {package}.")
        filenames = [item["filename"] for item in files]
        stem = f"{package.replace('-', '_')}-{record['version']}"
        if set(filenames) != {f"{stem}-py3-none-any.whl", f"{stem}.tar.gz"}:
            raise ValueError(f"Unexpected distribution names: {package}.")
        for item in files:
            path = directory / package / item["filename"]
            if (path.is_symlink() or path.resolve().parent != directory.resolve() / package
                    or path.stat().st_size != item["size"] or digest(path) != item["sha256_digest"]):
                raise ValueError(f"CI artifact digest mismatch: {path.name}.")


def image_context(artifacts: Path, output: Path) -> None:
    """Reuse tested wheels; never rebuild a dependency in docker build."""
    artifacts, output = artifacts.resolve(), output.resolve()
    manifest = json.loads((artifacts / "manifest.json").read_text())
    revision = run("git", "rev-parse", "HEAD", capture=True)
    if manifest.get("revision") != revision:
        raise ValueError("Image inputs must match this checkout's exact commit.")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        if (os.environ.get("GITHUB_SHA") != revision
                or run("git", "status", "--porcelain", capture=True)):
            raise ValueError("CI image preparation requires a clean checkout matching GITHUB_SHA.")
        for field, name in (("repository", "GITHUB_REPOSITORY"), ("run_id", "GITHUB_RUN_ID"),
                            ("run_attempt", "GITHUB_RUN_ATTEMPT")):
            if not os.environ.get(name) or manifest.get(field) != os.environ[name]:
                raise ValueError("Use distributions from this exact CI run and attempt; rerun all jobs if necessary.")
    verify_distribution_files(manifest, artifacts)
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Image context must be empty; choose a new --out directory.")
    output.mkdir(parents=True, exist_ok=True)
    wheels = output / "wheels"
    wheels.mkdir()
    for package, record in manifest["packages"].items():
        wheel = next(item for item in record["files"] if item["filename"].endswith(".whl"))
        target = wheels / wheel["filename"]
        shutil.copyfile(artifacts / package / wheel["filename"], target)
        if digest(target) != wheel["sha256_digest"]:
            raise ValueError("An input changed while copying; discard this context and retry.")
    write_json(output / "inputs.json", manifest)
    print(f"Prepared {len(PACKAGES)} tested wheels at {output}; no packages rebuilt.")
    if output == ROOT / ".orbit-image-context":
        print("Next, on your Docker runner: docker build -t meridian-billing-preview .")
    else:
        print("The root Dockerfile expects this directory at .orbit-image-context in its build checkout.")


def validation_tools(output: Path, source: Path | None) -> None:
    """Install the existing Orbit receiver/reporting adapter and Meridian checks."""
    if source is None:
        record = state_dir() / "orbit-source.json"
        if not record.exists():
            raise ValueError("Run ./demo setup first, or provide --source /path/to/orbit.")
        source = Path(json.loads(record.read_text())["path"])
    examples = source.expanduser().resolve() / "project/python-package-registry/examples/validation-hooks"
    files = {
        "orbit-validate.sh": examples / "orbit-validate.sh",
        "receiver/orbit_webhook_receiver.py": examples / "receiver/orbit_webhook_receiver.py",
        "README.md": examples / "README.md",
        "meridian-validation.sh": ROOT / "scripts/meridian-validation.sh",
    }
    if any(not path.is_file() for path in files.values()):
        raise ValueError("Use the current Orbit source with version-2 validation hooks; run ./demo setup.")
    output = output.expanduser().resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Validation tools destination must be empty; existing receiver data is preserved.")
    output.mkdir(parents=True, exist_ok=True)
    for name, path in files.items():
        target = output / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(path, target)
        if name.endswith(".sh"):
            target.chmod(0o755)
    print(f"Validation tools: {output}\nNext: tutorial/images/validation.md. No receiver was started.")


def evidence_for(candidate: dict, record: dict, result: dict, package: str) -> dict:
    expected = sorted(record["files"], key=lambda f: f["filename"])
    actual = sorted(({key: item[key] for key in ("filename", "size", "sha256_digest")}
                     for item in candidate["artifacts"]), key=lambda f: f["filename"])
    if candidate["package"] != package or candidate["version"] != record["version"] or actual != expected:
        raise ValueError("Orbit's candidate differs from the tested CI artifacts; no evidence was submitted.")
    return {"outcome": "passed", "provider": "github-actions",
            "run_id": f"{result['databaseId']}/attempts/{result['attempt']}",
            "revision": result["headSha"], "details_url": result["url"],
            "candidate_manifest_hash": candidate["manifest_hash"]}


def publish(selection: str, run_id: str | None) -> None:
    if run("git", "status", "--porcelain", capture=True):
        raise ValueError("Commit your changes before publishing; the release must match CI exactly.")
    revision = run("git", "rev-parse", "HEAD", capture=True)
    repository = github_repository(run("git", "remote", "get-url", "origin", capture=True))
    if run_id is None:
        runs = json.loads(run("gh", "run", "list", "--repo", repository, "--workflow", "ci.yml",
                              "--commit", revision, "--limit", "20",
                              "--json", "databaseId,event", capture=True))
        runs = [result for result in runs if result["event"] in {"push", "workflow_dispatch"}]
        if not runs:
            raise ValueError("No CI run for this commit. Enable Actions and push to your fork, then rerun.")
        run_id = str(runs[0]["databaseId"])
    result = json.loads(run("gh", "run", "view", run_id, "--repo", repository,
                           "--json", "databaseId,headSha,status,conclusion,url,event,workflowName,attempt",
                           capture=True))
    verify_run(result, repository, revision)
    connection = context()
    if connection.get("credential", {}).get("status") not in {"stored", "verified"}:
        raise ValueError("Connect this checkout first: registry init")
    checkpoint_key = hashlib.sha256(
        f"{connection['origin']}:{connection['tenant_id']}:{repository}:{run_id}:{result['attempt']}".encode()
    ).hexdigest()[:32]
    checkpoint = state_dir() / f"release-{checkpoint_key}.json"
    uploaded = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
    with tempfile.TemporaryDirectory(prefix="meridian-ci-") as temp:
        directory = Path(temp)
        run("gh", "run", "download", run_id, "--repo", repository, "--name", ARTIFACT_NAME, "--dir", directory)
        manifest = json.loads((directory / "manifest.json").read_text())
        verify_manifest(manifest, result, repository, directory)
        selected = ["meridian-billing-sdk"] if selection == "sdk" else list(PACKAGES)[1:]
        for package in selected:
            record = manifest["packages"][package]
            profile = "meridian-auth-release" if package == "meridian-auth" else "meridian-billing-release"
            credential = ["--profile", profile, "--tenant", connection["tenant_id"]]
            # The same package/version in this CI run always resumes the same promotion.
            identity = f"{repository}:{run_id}:{result['attempt']}:{package}:{record['version']}"
            key = "meridian:" + hashlib.sha256(identity.encode()).hexdigest()[:48]
            for item in record["files"]:
                if uploaded.get(item["filename"]) == item["sha256_digest"]:
                    continue
                run("registry", "publish", *credential, "--workspace", ROOT, "--package", package,
                    directory / package / item["filename"])
                uploaded[item["filename"]] = item["sha256_digest"]
                write_json(checkpoint, uploaded)
            command = ["registry", "promote", package, record["version"], *credential, "--idempotency-key", key]
            promotion = json.loads(run(*command, "--json", capture=True))
            evidence = evidence_for(promotion["candidate"], record, result, package)
            if promotion["state"] != "succeeded":
                evidence_path = directory / "ci-evidence.json"
                write_json(evidence_path, evidence)
                run(*command, "--ci-evidence", evidence_path)
                approval_url = (f"{connection['origin']}/+app/t/{connection['tenant_id']}"
                                f"/releases/{promotion['id']}")
                print(
                    f"\nACTION NEEDED: {package} {record['version']} is waiting for your approval.\n"
                    f"  1. Open this page in your browser, signed in as an approver:\n"
                    f"     {approval_url}\n"
                    f"  2. Review the candidate and press \"Approve exact candidate\".\n"
                    f"  The helper waits up to 5 minutes for that approval. If it times out, approve\n"
                    f"  the page and rerun this command; it resumes the same promotion.\n",
                    flush=True,
                )
                run(*command, "--wait")
            print(f"{package} {record['version']}: production ready.")
    write_json(state_dir() / "last-release.json",
               {"selection": selection, "run_url": result["url"], "revision": revision})


def install(selection: str, customer: str | None) -> None:
    package = "meridian-billing-sdk" if selection == "sdk" else "meridian-billing-core"
    executable = "meridian-invoices" if selection == "sdk" else "meridian-billing"
    with tempfile.TemporaryDirectory(prefix="meridian-consumer-") as temp:
        folder = Path(temp)
        run("uv", "venv", folder / ".venv", "--python", "3.12", cwd=folder)
        run("uv", "pip", "install", "--python", folder / ".venv/bin/python", "--no-cache",
            f"{package}=={version(package)}", cwd=folder)
        args = ["--customer", customer] if customer else []
        run(folder / ".venv/bin" / executable, ROOT / "examples/invoices.json", *args, cwd=folder)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup", help="Install the tested registry CLI and Launchpad").add_argument(
        "--source", type=Path)
    commands.add_parser("build", help="Build and test real distributions locally").add_argument("--out", type=Path)
    image = commands.add_parser("image-context", help="Prepare the Docker context from the exact tested wheels")
    image.add_argument("--artifacts", type=Path, required=True)
    image.add_argument("--out", type=Path, default=ROOT / ".orbit-image-context")
    validator = commands.add_parser("validation-tools", help="Copy Orbit's receiver/reporting tools and Meridian checks")
    validator.add_argument("--out", type=Path, required=True)
    validator.add_argument("--source", type=Path)
    release = commands.add_parser("publish", help="Use real CI artifacts; wait for Orbit approval")
    release.add_argument("selection", choices=["sdk", "bundle"])
    release.add_argument("--run", help="GitHub run ID; defaults to the latest push run for HEAD")
    login = commands.add_parser("login", help="Save a scoped release key through registry's hidden prompt")
    login.add_argument("group", choices=["billing", "auth"])
    consumer = commands.add_parser("install", help="Download from Orbit in a fresh environment and run invoices")
    consumer.add_argument("selection", choices=["sdk", "billing"])
    consumer.add_argument("--customer", help="SDK filter, after the release exercise")
    commands.add_parser("status", help="Show checkout status and last completed release")
    launchpad = commands.add_parser("launchpad", help="Run the pinned Launchpad copy")
    launchpad.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command == "setup":
        setup(args.source)
    elif args.command == "build":
        build(args.out or Path(tempfile.mkdtemp(prefix="meridian-build-")))
    elif args.command == "image-context":
        image_context(args.artifacts, args.out)
    elif args.command == "validation-tools":
        validation_tools(args.out, args.source)
    elif args.command == "publish":
        publish(args.selection, args.run)
    elif args.command == "login":
        connection = context()
        run("registry", "login", "--origin", connection["origin"], "--tenant", connection["tenant_id"],
            "--profile", f"meridian-{args.group}-release")
    elif args.command == "install":
        install(args.selection, args.customer)
    elif args.command == "status":
        run("registry", "context", "show")
        run("registry", "status")
        last = state_dir() / "last-release.json"
        if last.exists():
            record = json.loads(last.read_text())
            print(f"Last completed release: {record['selection']} · {record['revision'][:8]}\n{record['run_url']}")
    elif args.command == "launchpad":
        directory = Path(run("uv", "tool", "dir", capture=True))
        run(directory / "launchpad-uv/bin/launchpad", *args.arguments)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"demo: {error}", file=sys.stderr)
        sys.exit(1)

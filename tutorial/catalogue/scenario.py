#!/usr/bin/env python3
"""Prepare one catalogue scenario in a clean end-of-tutorial workspace.

The script deliberately edits only the exact files used by the Meridian demo.
Run it in an isolated clone, commit the result, then submit it with
``registry topology sync``.  Every scenario starts from the converged state at
the end of Part 4; scenarios are not cumulative.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable


ROOT_CONFIG = Path("pyproject.toml")
BILLING_APP = Path("project/billing/application/billing-api/pyproject.toml")
NOTIFY_APP = Path("project/notifications/application/notify-worker/orbit.toml")
BILLING_CLI = Path("project/billing/package/meridian-billing-cli")
RATELIMIT = Path("package/library/ratelimit/meridian-ratelimit")


class ScenarioError(RuntimeError):
    """A scenario could not be applied safely to this workspace."""


def _read(root: Path, relative: Path) -> str:
    path = root / relative
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ScenarioError(f"cannot read {relative}: {error}") from error


def _replace_once(root: Path, relative: Path, old: str, new: str) -> None:
    path = root / relative
    text = _read(root, relative)
    count = text.count(old)
    if count != 1:
        raise ScenarioError(
            f"expected one baseline block in {relative}, found {count}; "
            "start from a fresh converged end-of-tutorial clone"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def _unlink(root: Path, relative: Path) -> None:
    path = root / relative
    try:
        path.unlink()
    except OSError as error:
        raise ScenarioError(f"cannot remove {relative}: {error}") from error


def _run(root: Path, *command: str) -> None:
    try:
        subprocess.run(command, cwd=root, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise ScenarioError(f"{' '.join(command)} failed: {error}") from error


def _require_clean_workspace(root: Path) -> None:
    if not (root / ".git").exists():
        raise ScenarioError(f"{root} is not a Git checkout")
    status = subprocess.run(
        ("git", "status", "--porcelain"),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise ScenarioError(
            "the workspace is not clean; create a fresh isolated clone before "
            "preparing a catalogue scenario"
        )
    required = (
        ROOT_CONFIG,
        BILLING_APP,
        NOTIFY_APP,
        RATELIMIT / "pyproject.toml",
        RATELIMIT / "src/meridian_ratelimit/py.typed",
        Path("package/library/search/meridian-search/pyproject.toml"),
    )
    missing = [str(path) for path in required if not (root / path).is_file()]
    if missing:
        raise ScenarioError(
            "this is not the completed Part 4 workspace; missing " + ", ".join(missing)
        )


def pin(root: Path) -> None:
    _replace_once(
        root,
        ROOT_CONFIG,
        '[tool.orbit.registry.members.meridian-auth]\ntier = "public"',
        '[tool.orbit.registry.members.meridian-auth]\ntier = "public"\npin = true',
    )


def retier(root: Path) -> None:
    _replace_once(
        root,
        ROOT_CONFIG,
        '[tool.orbit.registry.members.meridian-notify]\ntier = "protected"',
        '[tool.orbit.registry.members.meridian-notify]\ntier = "private"',
    )


def resource_tiers(root: Path) -> None:
    _replace_once(
        root,
        ROOT_CONFIG,
        '[tool.orbit.registry.resources."project.notifications"]\n'
        'display_name = "Notifications"\n'
        'branches = ["protected", "private"]',
        '[tool.orbit.registry.resources."project.notifications"]\n'
        'display_name = "Notifications"\n'
        'branches = ["public", "protected", "private"]',
    )


def upstream_policy(root: Path) -> None:
    _replace_once(root, ROOT_CONFIG, 'upstream = "pypi"', 'upstream = "none"')



def retire_package(root: Path) -> None:
    _replace_once(
        root,
        ROOT_CONFIG,
        '\n[tool.orbit.registry.members.meridian-billing-cli]\n'
        'tier = "protected"\n',
        "\n",
    )
    _unlink(root, BILLING_CLI / "pyproject.toml")
    _unlink(root, BILLING_CLI / "src/meridian_billing_cli/__init__.py")
    _run(root, "uv", "lock")


def retire_resource(root: Path) -> None:
    _unlink(root, RATELIMIT / "pyproject.toml")
    _unlink(root, RATELIMIT / "src/meridian_ratelimit/__init__.py")
    _unlink(root, RATELIMIT / "src/meridian_ratelimit/py.typed")
    _run(root, "uv", "lock")


def suppress_reference(root: Path) -> None:
    _replace_once(
        root,
        ROOT_CONFIG,
        '[tool.orbit.registry.resources."project.billing"]\n'
        'branches = ["public", "protected", "private"]',
        '[tool.orbit.registry.resources."project.billing"]\n'
        'branches = ["public", "protected", "private"]\n'
        'remove_references = ["library.auth"]',
    )


def rename_anchored(root: Path) -> None:
    _replace_once(
        root,
        NOTIFY_APP,
        'name = "notify-worker"\nkind = "worker"',
        'name = "notify-dispatcher"\n'
        'application_key = "notify-worker"\n'
        'kind = "worker"',
    )


def rename_unanchored(root: Path) -> None:
    _replace_once(
        root,
        NOTIFY_APP,
        'name = "notify-worker"',
        'name = "notify-dispatcher"',
    )


def rename_uv_application_unanchored(root: Path) -> None:
    _replace_once(
        root,
        BILLING_APP,
        'name = "billing-api"',
        'name = "billing-service"',
    )
    _run(root, "uv", "lock")


def rehome_package(root: Path) -> None:
    _replace_once(
        root,
        ROOT_CONFIG,
        '[tool.orbit.registry.members.meridian-telemetry]\ntier = "private"',
        '[tool.orbit.registry.members.meridian-telemetry]\n'
        'tier = "private"\n'
        'resource = "library.config"',
    )


SCENARIOS: dict[str, Callable[[Path], None]] = {
    "pin": pin,
    "retier": retier,
    "resource-tiers": resource_tiers,
    "upstream-policy": upstream_policy,
    "retire-package": retire_package,
    "retire-resource": retire_resource,
    "suppress-reference": suppress_reference,
    "rename-anchored": rename_anchored,
    "rename-unanchored": rename_unanchored,
    "rename-uv-application-unanchored": rename_uv_application_unanchored,
    "rehome-package": rehome_package,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="prepare one isolated Meridian topology catalogue scenario"
    )
    parser.add_argument("scenario", choices=tuple(SCENARIOS))
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("."),
        help="clean completed Part 4 checkout (default: current directory)",
    )
    args = parser.parse_args()
    root = args.workspace.resolve()
    try:
        _require_clean_workspace(root)
        SCENARIOS[args.scenario](root)
    except (OSError, subprocess.CalledProcessError, ScenarioError) as error:
        print(f"catalogue scenario: {error}", file=sys.stderr)
        return 2
    print(f"Prepared catalogue scenario: {args.scenario}")
    print("Review the diff, then commit every changed file before plan or sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

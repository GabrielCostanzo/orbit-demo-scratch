"""Release boundaries use simulated provider results; these are never CI evidence."""

import copy
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "scripts/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

REPOSITORY = "example/orbit-demo"
RUN = {"databaseId": 42, "attempt": 1, "headSha": "a" * 40, "status": "completed",
       "conclusion": "success", "event": "push", "workflowName": "Build and test distributions",
       "url": f"https://github.com/{REPOSITORY}/actions/runs/42"}


def artifacts(directory):
    packages = {}
    for package in demo.PACKAGES:
        folder = directory / package
        folder.mkdir()
        version = demo.version(package)
        stem = f"{package.replace('-', '_')}-{version}"
        files = []
        for suffix in ["-py3-none-any.whl", ".tar.gz"]:
            path = folder / f"{stem}{suffix}"
            path.write_bytes(f"fixture:{path.name}".encode())
            files.append({"filename": path.name, "size": path.stat().st_size,
                          "sha256_digest": demo.digest(path)})
        packages[package] = {"version": version, "files": files}
    return {"repository": REPOSITORY, "run_id": "42", "run_attempt": "1",
            "revision": RUN["headSha"], "packages": packages}


class ServerCommitTests(unittest.TestCase):
    def test_reports_the_commit_the_origin_publishes(self):
        calls = []

        def fake_urlopen(url, timeout=None):
            calls.append((url, timeout))
            return io.BytesIO(json.dumps({"commit": "b" * 40, "build_number": 249}).encode())

        with patch("urllib.request.urlopen", fake_urlopen):
            self.assertEqual(demo.server_commit("https://orbit.example"), "b" * 40)
        self.assertEqual(calls, [("https://orbit.example/+version", 5)])

    def test_unreachable_or_unexpected_responses_never_raise(self):
        for body in [b"<html>not json</html>", json.dumps({"build_number": 249}).encode(),
                     json.dumps({"commit": 249}).encode(), json.dumps(["commit"]).encode()]:
            with (self.subTest(body=body),
                  patch("urllib.request.urlopen", lambda *args, **kwargs: io.BytesIO(body))):
                self.assertIsNone(demo.server_commit("https://orbit.example"))
        with patch("urllib.request.urlopen", side_effect=OSError("unreachable")):
            self.assertIsNone(demo.server_commit("https://orbit.example"))


class EvidenceTests(unittest.TestCase):
    def test_requires_successful_exact_revision_and_workflow(self):
        demo.verify_run(RUN, REPOSITORY, RUN["headSha"])
        for field, value in [("conclusion", "failure"), ("status", "in_progress"),
                             ("headSha", "b" * 40), ("event", "pull_request"),
                             ("workflowName", "Other workflow"), ("url", "https://github.com/other/run")]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                demo.verify_run({**RUN, field: value}, REPOSITORY, RUN["headSha"])

    def test_manifest_binds_exact_files_repository_revision_and_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = artifacts(folder)
            demo.verify_manifest(manifest, RUN, REPOSITORY, folder)
            for field, value in [("repository", "other/fork"), ("revision", "b" * 40),
                                 ("run_id", "43"), ("run_attempt", "2")]:
                with self.subTest(field=field), self.assertRaises(ValueError):
                    demo.verify_manifest({**manifest, field: value}, RUN, REPOSITORY, folder)
            file = next(folder.rglob("*.whl"))
            file.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                demo.verify_manifest(manifest, RUN, REPOSITORY, folder)

    def test_rejects_path_escape_and_unexpected_package_set(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            manifest = artifacts(folder)
            altered = copy.deepcopy(manifest)
            altered["packages"]["extra"] = {}
            with self.assertRaises(ValueError):
                demo.verify_manifest(altered, RUN, REPOSITORY, folder)
            first = next(iter(manifest["packages"].values()))
            first["files"][0]["filename"] = "../../outside.whl"
            with self.assertRaisesRegex(ValueError, "distribution names"):
                demo.verify_manifest(manifest, RUN, REPOSITORY, folder)

    def test_candidate_must_match_the_tested_artifact_set(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = artifacts(Path(temp))
            package = "meridian-billing-sdk"
            record = manifest["packages"][package]
            candidate = {"package": package, "version": record["version"],
                         "manifest_hash": "c" * 64, "artifacts": record["files"]}
            evidence = demo.evidence_for(candidate, record, RUN, package)
            self.assertEqual(evidence["revision"], RUN["headSha"])
            self.assertEqual(evidence["run_id"], "42/attempts/1")
            self.assertEqual(evidence["candidate_manifest_hash"], "c" * 64)
            altered = copy.deepcopy(candidate)
            altered["artifacts"][0]["sha256_digest"] = "d" * 64
            with self.assertRaises(ValueError):
                demo.evidence_for(altered, record, RUN, package)

    def test_origin_is_a_github_repository_not_an_arbitrary_download_host(self):
        for remote in ["https://github.com/example/orbit-demo.git", "git@github.com:example/orbit-demo.git"]:
            self.assertEqual(demo.github_repository(remote), REPOSITORY)
        with self.assertRaises(ValueError):
            demo.github_repository("https://other.example/example/orbit-demo.git")

    def test_publish_refuses_dirty_checkout_before_network_or_mutation(self):
        with patch.object(demo, "run", return_value=" M pyproject.toml") as run:
            with self.assertRaisesRegex(ValueError, "Commit your changes"):
                demo.publish("sdk", "42")
        run.assert_called_once_with("git", "status", "--porcelain", capture=True)

    def test_publish_refuses_bad_ci_before_reading_credentials_or_uploading(self):
        for change in [{"conclusion": "failure"}, {"headSha": "b" * 40}]:
            outputs = ["", RUN["headSha"], f"https://github.com/{REPOSITORY}.git",
                       json.dumps({**RUN, **change})]
            with (self.subTest(change=change),
                  patch.object(demo, "run", side_effect=outputs) as run,
                  patch.object(demo, "context") as context):
                with self.assertRaisesRegex(ValueError, "successful.*run"):
                    demo.publish("sdk", "42")
                context.assert_not_called()
                self.assertTrue(all(call.args[0] in {"git", "gh"} for call in run.call_args_list))

    def test_publish_refuses_tampered_download_before_any_registry_mutation(self):
        calls = []

        def fake_run(*args, **kwargs):
            args = [str(arg) for arg in args]
            calls.append(args)
            if args[:3] == ["git", "status", "--porcelain"]:
                return ""
            if args[:2] == ["git", "rev-parse"]:
                return RUN["headSha"]
            if args[:2] == ["git", "remote"]:
                return f"https://github.com/{REPOSITORY}.git"
            if args[:3] == ["gh", "run", "view"]:
                return json.dumps(RUN)
            if args[:3] == ["gh", "run", "download"]:
                directory = Path(args[args.index("--dir") + 1])
                manifest = artifacts(directory)
                next(directory.rglob("*.whl")).write_bytes(b"tampered")
                demo.write_json(directory / "manifest.json", manifest)
                return ""
            self.fail(f"Unexpected command: {args}")

        connection = {"origin": "https://orbit.example", "tenant_id": "tenant-id",
                      "credential": {"status": "verified"}}
        with (tempfile.TemporaryDirectory() as temp,
              patch.object(demo, "run", side_effect=fake_run),
              patch.object(demo, "context", return_value=connection),
              patch.object(demo, "state_dir", return_value=Path(temp))):
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                demo.publish("sdk", "42")
        self.assertTrue(all(args[0] in {"git", "gh"} for args in calls))

    def test_resume_reuses_uploads_and_waits_for_authoritative_production_success(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            calls = []
            waiting = True

            def fake_run(*args, **kwargs):
                nonlocal waiting
                args = [str(arg) for arg in args]
                calls.append(args)
                if args[:3] == ["git", "status", "--porcelain"]:
                    return ""
                if args[:2] == ["git", "rev-parse"]:
                    return RUN["headSha"]
                if args[:2] == ["git", "remote"]:
                    return f"https://github.com/{REPOSITORY}.git"
                if args[:3] == ["gh", "run", "view"]:
                    return json.dumps(RUN)
                if args[:3] == ["gh", "run", "download"]:
                    directory = Path(args[args.index("--dir") + 1])
                    demo.write_json(directory / "manifest.json", artifacts(directory))
                    return ""
                if args[:2] == ["registry", "promote"]:
                    if "--wait" in args and waiting:
                        waiting = False
                        raise subprocess.CalledProcessError(1, args)
                    if "--json" in args:
                        artifact_dir = state / "expected"
                        if not artifact_dir.exists():
                            artifact_dir.mkdir()
                        else:
                            return saved[0]
                        record = artifacts(artifact_dir)["packages"]["meridian-billing-sdk"]
                        candidate = {"package": "meridian-billing-sdk", "version": record["version"],
                                     "manifest_hash": "c" * 64, "artifacts": record["files"]}
                        saved.append(json.dumps({"id": "promotion-id", "state": "pending", "candidate": candidate}))
                        return saved[0]
                return ""

            saved = []
            connection = {"origin": "https://orbit.example", "tenant_id": "tenant-id",
                          "credential": {"status": "verified"}}
            with (redirect_stdout(io.StringIO()), patch.object(demo, "run", side_effect=fake_run),
                  patch.object(demo, "context", return_value=connection),
                  patch.object(demo, "state_dir", return_value=state)):
                with self.assertRaises(subprocess.CalledProcessError):
                    demo.publish("sdk", "42")
                self.assertFalse((state / "last-release.json").exists())
                demo.publish("sdk", "42")
            self.assertEqual(sum(args[:2] == ["registry", "publish"] for args in calls), 2)
            self.assertEqual(sum("--wait" in args for args in calls), 2)
            self.assertTrue((state / "last-release.json").exists())

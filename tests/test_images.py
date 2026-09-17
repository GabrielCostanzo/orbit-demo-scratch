"""Image-input and validation boundaries; simulated metadata is not live CI proof."""

from contextlib import redirect_stdout
import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_demo import artifacts, RUN, REPOSITORY

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("image_demo", ROOT / "scripts/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class ImageContextTests(unittest.TestCase):
    def prepare(self, folder):
        source = folder / "artifacts"
        source.mkdir()
        manifest = artifacts(source)
        demo.write_json(source / "manifest.json", manifest)
        return source, folder / "context", manifest

    def test_context_reuses_exact_wheels_without_a_rebuild(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output, manifest = self.prepare(Path(temp))
            with (patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}),
                  patch.object(demo, "run", return_value=RUN["headSha"]) as run,
                  redirect_stdout(io.StringIO())):
                demo.image_context(source, output)
            run.assert_called_once_with("git", "rev-parse", "HEAD", capture=True)
            self.assertEqual(json.loads((output / "inputs.json").read_text()), manifest)
            self.assertEqual(len(list((output / "wheels").iterdir())), len(demo.PACKAGES))
            for package, record in manifest["packages"].items():
                wheel = next(item for item in record["files"] if item["filename"].endswith(".whl"))
                self.assertEqual((output / "wheels" / wheel["filename"]).read_bytes(),
                                 (source / package / wheel["filename"]).read_bytes())

    def test_rejects_wrong_commit_or_modified_wheel_before_writing_context(self):
        for modified in (False, True):
            with self.subTest(modified=modified), tempfile.TemporaryDirectory() as temp:
                source, output, manifest = self.prepare(Path(temp))
                if modified:
                    next(source.rglob("*.whl")).write_bytes(b"modified wheel")
                with (patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}),
                      patch.object(demo, "run", return_value=RUN["headSha"] if modified else "b" * 40)):
                    with self.assertRaises(ValueError):
                        demo.image_context(source, output)
                self.assertFalse(output.exists())

    def test_ci_inputs_must_match_current_run_attempt_and_clean_checkout(self):
        env = {"GITHUB_ACTIONS": "true", "GITHUB_SHA": RUN["headSha"],
               "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_RUN_ID": "42", "GITHUB_RUN_ATTEMPT": "1"}
        for change, dirty in [({}, ""), ({"GITHUB_REPOSITORY": "another/repo"}, ""),
                              ({"GITHUB_RUN_ID": "43"}, ""), ({"GITHUB_RUN_ATTEMPT": "2"}, ""),
                              ({"GITHUB_SHA": "b" * 40}, ""), ({}, " M Dockerfile")]:
            with self.subTest(change=change, dirty=dirty), tempfile.TemporaryDirectory() as temp:
                source, output, _ = self.prepare(Path(temp))
                with (patch.dict(os.environ, {**env, **change}),
                      patch.object(demo, "run", side_effect=[RUN["headSha"], dirty]),
                      redirect_stdout(io.StringIO())):
                    if change or dirty:
                        with self.assertRaises(ValueError):
                            demo.image_context(source, output)
                        self.assertFalse(output.exists())
                    else:
                        demo.image_context(source, output)

    def test_existing_context_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output, _ = self.prepare(Path(temp))
            output.mkdir()
            marker = output / "keep"
            marker.write_text("existing")
            with (patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}),
                  patch.object(demo, "run", return_value=RUN["headSha"])):
                with self.assertRaisesRegex(ValueError, "must be empty"):
                    demo.image_context(source, output)
            self.assertEqual(marker.read_text(), "existing")


class ValidationCommandTests(unittest.TestCase):
    @staticmethod
    def definition(key):
        value = {"workflow": "meridian/billing-" + key, "version": "1", "parameters": {}}
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def test_tag_unknown_check_or_wrong_definition_never_calls_docker(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            docker = folder / "docker"
            docker.write_text('#!/bin/sh\ntouch "$DOCKER_CALLED"\nexit 0\n')
            docker.chmod(0o755)
            marker = folder / "called"
            for image, key, definition in [("registry.example/app:latest", "smoke", self.definition("smoke")),
                                          ("registry.example/app@sha256:" + "a" * 64, "unknown", "a" * 64),
                                          ("registry.example/app@sha256:" + "a" * 64, "smoke", "a" * 64)]:
                environment = {**os.environ, "ORBIT_IMAGE": image, "ORBIT_VALIDATION_KEY": key,
                               "ORBIT_VALIDATION_DEFINITION_SHA256": definition,
                               "PATH": str(folder) + os.pathsep + os.environ["PATH"],
                               "DOCKER_CALLED": str(marker)}
                result = subprocess.run(["sh", str(ROOT / "scripts/meridian-validation.sh")],
                                        env=environment, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(marker.exists())

    def test_failed_smoke_preserves_exit_and_cleans_only_its_container(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            docker = folder / "docker"
            docker.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$DOCKER_CALLS"\n'
                              'case "$1" in run) echo owned-test-container ;; exec) exit 7 ;; rm) exit 0 ;; esac\n')
            docker.chmod(0o755)
            calls = folder / "calls"
            environment = {**os.environ, "ORBIT_IMAGE": "registry.example/app@sha256:" + "a" * 64,
                           "ORBIT_VALIDATION_KEY": "smoke", "DOCKER_CALLS": str(calls),
                           "ORBIT_VALIDATION_DEFINITION_SHA256": self.definition("smoke"),
                           "PATH": str(folder) + os.pathsep + os.environ["PATH"]}
            result = subprocess.run(["sh", str(ROOT / "scripts/meridian-validation.sh")], env=environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 7)
            lines = calls.read_text().splitlines()
            self.assertIn("--network none --read-only", lines[0])
            self.assertEqual(lines[-1], "rm --force owned-test-container")

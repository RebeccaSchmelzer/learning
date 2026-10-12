import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import review


def answer(score=0, confidence=0.9, security=0.1):
    low = int(score)
    probabilities = {str(i): 0 for i in range(4)}
    probabilities[str(low)] = 1 - (score - low)
    if low < 3:
        probabilities[str(low + 1)] = score - low
    return {
        "model": "jev-test",
        "answers": {
            "risk": {"type": "score", "score": score, "confidence": confidence,
                     "legend": dict(enumerate(review.CRITERIA)), "probabilities": probabilities},
            "security_sensitive": {"type": "noul", "noul": security},
        },
    }


def response(**kwargs):
    result = answer(**kwargs)
    result["answers"]["risk"]["legend"] = {str(k): v for k, v in result["answers"]["risk"]["legend"].items()}
    return result


class PolicyTests(unittest.TestCase):
    def evaluate(self, value, **kwargs):
        return review.evaluate(value, "base", "sha", **kwargs)

    def test_thresholds_and_uncertainty(self):
        self.assertEqual(self.evaluate(response(score=1, confidence=.8, security=.2))["status"], "pass")
        for kwargs in ({"score": 1.001}, {"confidence": .799}, {"security": .201}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.evaluate(response(**kwargs))["status"], "review_required")
        self.assertTrue(self.evaluate(response(security=.5))["security_flagged"])

    def test_fixture_never_passes(self):
        self.assertEqual(self.evaluate(response(), simulated=True)["status"], "simulated_review_required")

    def test_invalid_numeric_values_fail_closed(self):
        for field in ("score", "confidence"):
            for value in (True, None, "0", float("nan"), float("inf"), -1, 10**500):
                with self.subTest(field=field, value=str(value)):
                    value_response = response()
                    value_response["answers"]["risk"][field] = value
                    with self.assertRaises(review.GateError):
                        self.evaluate(value_response)
        value_response = response()
        value_response["answers"]["security_sensitive"]["noul"] = False
        with self.assertRaises(review.GateError):
            self.evaluate(value_response)

    def test_response_shape_and_distribution_validation(self):
        valid = response()
        mutations = [
            lambda r: r["answers"].pop("risk"),
            lambda r: r["answers"]["risk"].update(type="choice"),
            lambda r: r["answers"]["risk"].update(score=1),
            lambda r: r["answers"]["risk"]["probabilities"].update({"0": .5}),
            lambda r: r["answers"]["risk"]["probabilities"].pop("3"),
            lambda r: r["answers"]["risk"]["legend"].update({"0": "altered"}),
        ]
        for mutate in mutations:
            invalid = copy.deepcopy(valid)
            mutate(invalid)
            with self.assertRaises(review.GateError):
                self.evaluate(invalid)


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.source = self.repo / "README.md"
        self.source.write_text("hello\n")
        self.git("add", "README.md")
        self.git("commit", "-qm", "initial")
        self.source.write_text("hello world\n")
        self.patch_file = self.root / "change.patch"
        self.patch_file.write_text(self.git("diff"))
        self.git("checkout", "--", "README.md")
        self.output = self.root / "report.json"
        self.fixture = self.root / "fixture.json"
        self.fixture.write_text(json.dumps(response()))

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args]).decode()

    def run_review(self, *extra, repo=None, output=None, patch_file=None):
        args = ["--repo", str(repo or self.repo), "--patch", str(patch_file or self.patch_file),
                "--output", str(output or self.output), *extra]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return review.main(args)

    def stale_pass(self):
        self.output.write_text('{"status":"pass"}')

    def test_live_response_and_artifact_identity(self):
        with patch.object(review, "call_jev", return_value=response()):
            self.assertEqual(self.run_review(), 0)
        report = json.loads(self.output.read_text())
        self.assertEqual(report["base_commit"], self.git("rev-parse", "HEAD").strip())
        self.assertEqual(len(report["patch_sha256"]), 64)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_fixture_exits_review_and_preview_removes_stale_report(self):
        self.assertEqual(self.run_review("--response-fixture", str(self.fixture)), 1)
        self.assertEqual(json.loads(self.output.read_text())["status"], "simulated_review_required")
        self.stale_pass()
        with patch.object(review, "call_jev") as network:
            self.assertEqual(self.run_review("--show-request"), 0)
            network.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_missing_invalid_and_oversize_patch_overwrite_stale_pass(self):
        for data in (b"", b"garbage", b"x" * (review.MAX_PATCH_BYTES + 1), b"\xff"):
            self.patch_file.write_bytes(data)
            self.stale_pass()
            self.assertEqual(self.run_review(), 2)
            self.assertEqual(json.loads(self.output.read_text())["status"], "error")
        self.patch_file.unlink()
        self.stale_pass()
        self.assertEqual(self.run_review(), 2)
        self.assertEqual(json.loads(self.output.read_text())["status"], "error")

    def test_dirty_untracked_repo_and_api_error_fail_closed(self):
        (self.repo / "extra").write_text("untracked")
        self.stale_pass()
        self.assertEqual(self.run_review(), 2)
        self.assertEqual(json.loads(self.output.read_text())["status"], "error")
        (self.repo / "extra").unlink()
        with patch.object(review, "call_jev", side_effect=review.GateError("Jev HTTP error 401.")):
            self.assertEqual(self.run_review(), 2)
        self.assertEqual(json.loads(self.output.read_text())["status"], "error")

    def test_stale_repository_and_patch_during_request_fail_closed(self):
        def mutate_repo(payload):
            self.source.write_text("changed\n")
            return response()
        with patch.object(review, "call_jev", side_effect=mutate_repo):
            self.assertEqual(self.run_review(), 2)
        self.git("checkout", "--", "README.md")
        def mutate_patch(payload):
            self.patch_file.write_text("different")
            return response()
        with patch.object(review, "call_jev", side_effect=mutate_patch):
            self.assertEqual(self.run_review(), 2)

    def test_output_cannot_overwrite_repo_from_subdirectory_or_input(self):
        subdir = self.repo / "subdir"
        subdir.mkdir()
        original = self.source.read_text()
        self.assertEqual(self.run_review(repo=subdir, output=self.source), 2)
        self.assertEqual(self.source.read_text(), original)
        original_patch = self.patch_file.read_bytes()
        self.assertEqual(self.run_review(output=self.patch_file), 2)
        self.assertEqual(self.patch_file.read_bytes(), original_patch)


if __name__ == "__main__":
    unittest.main()

import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("produce", ROOT / "produce.py")
produce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(produce)

PATCH = b'''diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1 +1 @@
-print("hello")
+print("hello, world")
'''


class ProduceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Tests")
        (self.repo / "hello.py").write_text('print("hello")\n')
        self.git("add", "hello.py")
        self.git("commit", "-qm", "initial")
        self.task = self.root / "task.txt"
        self.task.write_text("Improve the greeting")
        self.output = self.root / "change.patch"

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], stderr=subprocess.PIPE)

    def agent(self, code):
        return [sys.executable, "-c", code]

    def build(self, code, **kwargs):
        return produce.produce(self.repo, self.task, self.output, self.agent(code), **kwargs)

    def test_success_validates_without_applying_and_passes_task(self):
        code = "import sys; assert sys.stdin.read() == 'Improve the greeting'; sys.stdout.buffer.write(" + repr(PATCH) + ")"
        report = self.build(code)
        self.assertEqual(self.output.read_bytes(), PATCH)
        self.assertEqual(report["sha256"], hashlib.sha256(PATCH).hexdigest())
        self.assertEqual(report["base_commit"], self.git("rev-parse", "HEAD").decode().strip())
        self.assertEqual((self.repo / "hello.py").read_text(), 'print("hello")\n')
        self.assertEqual(self.git("status", "--porcelain"), b"")

    def test_invalid_or_empty_patch_does_not_replace_existing_output(self):
        self.output.write_bytes(b"previous")
        for patch in (b"", b"not a patch"):
            with self.subTest(patch=patch), self.assertRaises(produce.ProduceError):
                self.build("import sys; sys.stdout.buffer.write(" + repr(patch) + ")")
            self.assertEqual(self.output.read_bytes(), b"previous")

    def test_rejects_dirty_and_untracked_files_before_agent_runs(self):
        (self.repo / "untracked").write_text("x")
        with self.assertRaisesRegex(produce.ProduceError, "clean"):
            self.build("raise RuntimeError('must not run')")
        self.assertFalse(self.output.exists())

    def test_detected_mutations_are_left_for_inspection(self):
        with self.assertRaisesRegex(produce.ProduceError, "clean"):
            self.build("from pathlib import Path; Path('hello.py').write_text('changed'); print('diff')")
        self.assertEqual((self.repo / "hello.py").read_text(), "changed")
        self.assertFalse(self.output.exists())

    def test_failed_agent_does_not_leak_output(self):
        with self.assertRaisesRegex(produce.ProduceError, "^Patch agent failed$"):
            self.build("import sys; print('secret'); print('secret', file=sys.stderr); sys.exit(1)")

    def test_timeout(self):
        with self.assertRaisesRegex(produce.ProduceError, "timed out"):
            self.build("import time; time.sleep(3)", timeout=0.05)

    def test_rejects_output_inside_repository(self):
        for path in (self.repo / "hello.py", self.repo / "new.patch"):
            with self.subTest(path=path), self.assertRaisesRegex(produce.ProduceError, "outside"):
                produce.produce(self.repo, self.task, path, self.agent("print('diff')"))

    def test_rejects_output_overwriting_task_before_agent_runs(self):
        with self.assertRaisesRegex(produce.ProduceError, "differ from the task"):
            produce.produce(self.repo, self.task, self.task,
                            self.agent("raise RuntimeError('must not run')"))
        self.assertEqual(self.task.read_text(), "Improve the greeting")

    def test_rejects_changed_base_even_when_clean(self):
        code = "import subprocess; subprocess.run(['git', 'commit', '--allow-empty', '-qm', 'agent commit'], check=True)"
        with self.assertRaisesRegex(produce.ProduceError, "base commit"):
            self.build(code)

    def test_cli_emits_json_error_and_exit_two(self):
        result = subprocess.run([
            sys.executable, str(ROOT / "produce.py"), "--repo", str(self.repo),
            "--task-file", str(self.task), "--output", str(self.output),
            "--", sys.executable, "-c", "print('invalid')",
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('"status": "error"', result.stdout)
        self.assertNotIn("invalid", result.stdout)


if __name__ == "__main__":
    unittest.main()

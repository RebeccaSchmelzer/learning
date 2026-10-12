#!/usr/bin/env python3
"""Ask an external patch agent for a diff without changing its target repository."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile


class ProduceError(Exception):
    pass


def run_git(repo, *args, input_data=None):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], input=input_data,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProduceError("Git command could not complete") from exc
    if result.returncode:
        raise ProduceError("Git validation failed")
    return result.stdout


def assert_clean(repo):
    if run_git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ProduceError("Target repository must be clean, including untracked files")


def produce(repo, task_file, output, agent, timeout=120):
    repo = Path(repo).resolve()
    task_file = Path(task_file).resolve()
    output = Path(output).resolve()
    if output == task_file:
        raise ProduceError("Patch output must differ from the task file")
    root = Path(os.fsdecode(run_git(repo, "rev-parse", "--show-toplevel")).strip()).resolve()
    repo = root
    if output == root or root in output.parents:
        raise ProduceError("Patch output must be outside the target Git worktree")
    if not agent:
        raise ProduceError("Provide an agent command after --")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ProduceError("Timeout must be finite and positive")
    assert_clean(repo)
    base_commit = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    try:
        task = task_file.read_bytes()
    except OSError as exc:
        raise ProduceError("Could not read task file") from exc
    if not task.strip():
        raise ProduceError("Task file is empty")

    failure = None
    patch = b""
    try:
        result = subprocess.run(
            agent, input=task, cwd=repo, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False, shell=False,
        )
        if result.returncode:
            failure = "Patch agent failed"
        else:
            patch = result.stdout
    except subprocess.TimeoutExpired:
        failure = "Patch agent timed out"
    except OSError:
        failure = "Could not start patch agent"

    # Inspect even on failure: the agent may have left edits for the user to review.
    assert_clean(repo)
    if run_git(repo, "rev-parse", "HEAD").decode("ascii").strip() != base_commit:
        raise ProduceError("Patch agent changed the repository base commit")
    if failure:
        raise ProduceError(failure)
    if not patch.strip():
        raise ProduceError("Patch agent returned an empty patch")
    run_git(repo, "apply", "--check", "--", "-", input_data=patch)
    assert_clean(repo)

    temporary = None
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(patch)
        os.replace(temporary, output)
    except OSError as exc:
        raise ProduceError("Could not save patch") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {
        "status": "ok", "patch": str(output), "base_commit": base_commit,
        "sha256": hashlib.sha256(patch).hexdigest(), "bytes": len(patch),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--task-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=120,
                        help="Agent timeout in seconds (default: 120)")
    parser.add_argument("agent", nargs=argparse.REMAINDER,
                        help="Agent executable and arguments after --")
    args = parser.parse_args(argv)
    agent = args.agent[1:] if args.agent[:1] == ["--"] else args.agent
    try:
        report = produce(args.repo, args.task_file, args.output, agent, args.timeout)
    except ProduceError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())

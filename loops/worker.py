"""Background worker: claims queued jobs, performs them, and stores results."""

from __future__ import annotations

import os
import signal
import socket
import time
from collections.abc import Callable
from typing import Any

from config import DATABASE_PATH, JOB_LEASE_SECONDS, WORKER_POLL_SECONDS
from queue_store import JobStore


def uppercase(payload: dict[str, Any]) -> dict[str, Any]:
    return {"text": payload["text"].upper()}


def reverse(payload: dict[str, Any]) -> dict[str, Any]:
    return {"text": payload["text"][::-1]}


def word_count(payload: dict[str, Any]) -> dict[str, Any]:
    words = payload["text"].split()
    return {"count": len(words)}


PROCESSORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "uppercase": uppercase,
    "reverse": reverse,
    "word_count": word_count,
}


class Worker:
    def __init__(self, store: JobStore, poll_seconds: float, lease_seconds: int):
        self.store = store
        self.poll_seconds = poll_seconds
        self.lease_seconds = lease_seconds
        self.worker_id = f"{socket.gethostname()}-{os.getpid()}"
        self.running = True

    def stop(self, _signal: int | None = None, _frame: object | None = None) -> None:
        self.running = False

    def run(self) -> None:
        print(f"Worker {self.worker_id} started")
        print(f"Queue database: {self.store.database_path}")
        while self.running:
            job = self.store.claim_job(self.worker_id, self.lease_seconds)
            if job is None:
                time.sleep(self.poll_seconds)
                continue
            self.process(job)
        print("Worker stopped")

    def process(self, job: dict[str, Any]) -> None:
        print(
            f"Claimed {job['id']} ({job['task']}, "
            f"attempt {job['attempts']}/{job['max_attempts']})"
        )
        try:
            processor = PROCESSORS[job["task"]]
            result = processor(job["payload"])
            self.store.complete_job(job["id"], result)
            print(f"Completed {job['id']}")
        except Exception as error:
            new_status = self.store.fail_job(job["id"], str(error))
            print(f"{new_status.title()} {job['id']}: {error}")


def main() -> None:
    worker = Worker(
        JobStore(DATABASE_PATH),
        poll_seconds=WORKER_POLL_SECONDS,
        lease_seconds=JOB_LEASE_SECONDS,
    )
    signal.signal(signal.SIGINT, worker.stop)
    signal.signal(signal.SIGTERM, worker.stop)
    worker.run()


if __name__ == "__main__":
    main()


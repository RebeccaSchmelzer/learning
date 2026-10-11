from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from queue_store import JobStore


class JobStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database = Path(self.temporary_directory.name) / "test.db"
        self.store = JobStore(database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_job_moves_from_queued_to_completed(self) -> None:
        created = self.store.create_job("uppercase", {"text": "hello"})
        self.assertEqual(created["status"], "queued")

        claimed = self.store.claim_job("worker-1")
        self.assertIsNotNone(claimed)
        assert claimed is not None
        self.assertEqual(claimed["id"], created["id"])
        self.assertEqual(claimed["status"], "processing")
        self.assertEqual(claimed["attempts"], 1)

        self.store.complete_job(claimed["id"], {"text": "HELLO"})
        completed = self.store.get_job(claimed["id"])
        assert completed is not None
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["result"], {"text": "HELLO"})

    def test_failed_job_retries_then_stops(self) -> None:
        created = self.store.create_job(
            "uppercase", {"text": "hello"}, max_attempts=2
        )

        first = self.store.claim_job("worker-1")
        assert first is not None
        self.assertEqual(
            self.store.fail_job(first["id"], "temporary", retry_delay=0),
            "queued",
        )

        second = self.store.claim_job("worker-1")
        assert second is not None
        self.assertEqual(
            self.store.fail_job(second["id"], "permanent", retry_delay=0),
            "failed",
        )

        failed = self.store.get_job(created["id"])
        assert failed is not None
        self.assertEqual(failed["attempts"], 2)
        self.assertEqual(failed["error"], "permanent")

    def test_only_one_worker_can_claim_a_job(self) -> None:
        self.store.create_job("reverse", {"text": "abc"})
        self.assertIsNotNone(self.store.claim_job("worker-1"))
        self.assertIsNone(self.store.claim_job("worker-2"))


if __name__ == "__main__":
    unittest.main()


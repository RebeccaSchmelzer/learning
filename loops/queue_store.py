"""A tiny durable job queue backed by SQLite.

SQLite keeps this example dependency-free while still letting the API and worker
run as separate operating-system processes. A short write transaction makes
claiming a job atomic, so two workers cannot claim the same job.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def timestamp(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat(timespec="microseconds")


class JobStore:
    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    task TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('queued', 'processing', 'completed', 'failed')
                    ),
                    result TEXT,
                    error TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 3,
                    run_after TEXT NOT NULL,
                    locked_at TEXT,
                    worker_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS jobs_ready_idx
                ON jobs(status, run_after, created_at)
                """
            )

    def create_job(
        self, task: str, payload: dict[str, Any], max_attempts: int = 3
    ) -> dict[str, Any]:
        job_id = str(uuid.uuid4())
        now = timestamp()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    id, task, payload, status, attempts, max_attempts,
                    run_after, created_at, updated_at
                ) VALUES (?, ?, ?, 'queued', 0, ?, ?, ?, ?)
                """,
                (job_id, task, json.dumps(payload), max_attempts, now, now, now),
            )
        return self.get_job(job_id)  # type: ignore[return-value]

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
        return self._deserialize(row) if row else None

    def list_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._deserialize(row) for row in rows]

    def claim_job(
        self, worker_id: str, lease_seconds: int = 30
    ) -> dict[str, Any] | None:
        """Atomically reserve the oldest available job for one worker."""
        now = utc_now()
        now_text = timestamp(now)
        stale_before = timestamp(now - timedelta(seconds=lease_seconds))

        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")

            # A job abandoned by a crashed worker becomes available again.
            connection.execute(
                """
                UPDATE jobs
                SET status = 'queued', locked_at = NULL, worker_id = NULL,
                    run_after = ?, updated_at = ?,
                    error = 'Worker lease expired; job returned to queue'
                WHERE status = 'processing'
                  AND locked_at < ?
                  AND attempts < max_attempts
                """,
                (now_text, now_text, stale_before),
            )
            connection.execute(
                """
                UPDATE jobs
                SET status = 'failed', locked_at = NULL, worker_id = NULL,
                    updated_at = ?, error = 'Worker lease expired after final attempt'
                WHERE status = 'processing'
                  AND locked_at < ?
                  AND attempts >= max_attempts
                """,
                (now_text, stale_before),
            )

            row = connection.execute(
                """
                SELECT * FROM jobs
                WHERE status = 'queued' AND run_after <= ?
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (now_text,),
            ).fetchone()
            if row is None:
                connection.commit()
                return None

            connection.execute(
                """
                UPDATE jobs
                SET status = 'processing', attempts = attempts + 1,
                    locked_at = ?, worker_id = ?, updated_at = ?, error = NULL
                WHERE id = ?
                """,
                (now_text, worker_id, now_text, row["id"]),
            )
            claimed = connection.execute(
                "SELECT * FROM jobs WHERE id = ?", (row["id"],)
            ).fetchone()
            connection.commit()
            return self._deserialize(claimed)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def complete_job(self, job_id: str, result: dict[str, Any]) -> None:
        now = timestamp()
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE jobs
                SET status = 'completed', result = ?, error = NULL,
                    locked_at = NULL, worker_id = NULL, updated_at = ?
                WHERE id = ? AND status = 'processing'
                """,
                (json.dumps(result), now, job_id),
            )

    def fail_job(self, job_id: str, error: str, retry_delay: int = 2) -> str:
        """Record a failure and return the job's new status."""
        now = utc_now()
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT attempts, max_attempts FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown job: {job_id}")

            should_retry = row["attempts"] < row["max_attempts"]
            new_status = "queued" if should_retry else "failed"
            run_after = timestamp(now + timedelta(seconds=retry_delay))
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, error = ?, run_after = ?,
                    locked_at = NULL, worker_id = NULL, updated_at = ?
                WHERE id = ?
                """,
                (new_status, error[:1000], run_after, timestamp(now), job_id),
            )
            connection.commit()
            return new_status
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _deserialize(row: sqlite3.Row) -> dict[str, Any]:
        job = dict(row)
        job["payload"] = json.loads(job["payload"])
        job["result"] = json.loads(job["result"]) if job["result"] else None
        return job


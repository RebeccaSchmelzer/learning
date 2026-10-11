"""Configuration shared by the API and worker processes."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(
    os.environ.get("JOB_DATABASE", PROJECT_DIR / "data" / "jobs.db")
).expanduser()

API_HOST = os.environ.get("JOB_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("JOB_API_PORT", "8000"))

WORKER_POLL_SECONDS = float(os.environ.get("WORKER_POLL_SECONDS", "0.5"))
JOB_LEASE_SECONDS = int(os.environ.get("JOB_LEASE_SECONDS", "30"))


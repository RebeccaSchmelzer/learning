"""Producer HTTP API: validates requests and places jobs in the queue."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from config import API_HOST, API_PORT, DATABASE_PATH
from queue_store import JobStore


SUPPORTED_TASKS = {"uppercase", "reverse", "word_count"}
store = JobStore(DATABASE_PATH)


class JobAPIHandler(BaseHTTPRequestHandler):
    server_version = "JobAPI/1.0"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self.send_json(HTTPStatus.OK, {"status": "ok"})
            return

        if path == "/jobs":
            self.send_json(HTTPStatus.OK, {"jobs": store.list_jobs()})
            return

        if path.startswith("/jobs/"):
            job_id = path.removeprefix("/jobs/")
            job = store.get_job(job_id)
            if job is None:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Job not found")
                return
            self.send_json(HTTPStatus.OK, job)
            return

        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found")

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path != "/jobs":
            self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found")
            return

        try:
            body = self.read_json()
            task = body.get("task")
            payload = body.get("payload")
            max_attempts = body.get("max_attempts", 3)

            if task not in SUPPORTED_TASKS:
                raise ValueError(
                    f"task must be one of: {', '.join(sorted(SUPPORTED_TASKS))}"
                )
            if not isinstance(payload, dict):
                raise ValueError("payload must be a JSON object")
            if not isinstance(payload.get("text"), str):
                raise ValueError("payload.text must be a string")
            if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
                raise ValueError("max_attempts must be an integer")
            if not 1 <= max_attempts <= 10:
                raise ValueError("max_attempts must be between 1 and 10")

            job = store.create_job(task, payload, max_attempts)
            self.send_json(
                HTTPStatus.ACCEPTED,
                job,
                extra_headers={"Location": f"/jobs/{job['id']}"},
            )
        except (ValueError, json.JSONDecodeError) as error:
            self.send_error_json(HTTPStatus.BAD_REQUEST, str(error))

    def read_json(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise ValueError("Content-Type must be application/json")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Invalid Content-Length") from error
        if length <= 0 or length > 1_000_000:
            raise ValueError("Request body must be between 1 byte and 1 MB")
        body = json.loads(self.rfile.read(length))
        if not isinstance(body, dict):
            raise ValueError("Request body must be a JSON object")
        return body

    def send_json(
        self,
        status: HTTPStatus,
        body: dict[str, Any],
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        encoded = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(encoded)

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json(status, {"error": message})

    def log_message(self, format: str, *args: object) -> None:
        print(f"[api] {self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((API_HOST, API_PORT), JobAPIHandler)
    print(f"API listening at http://{API_HOST}:{API_PORT}")
    print(f"Queue database: {DATABASE_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI stopping")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()


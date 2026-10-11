# Two-component job processor

This project demonstrates the smallest useful asynchronous job system:

1. The **producer/API** accepts work over HTTP and writes it to a durable queue.
2. The **background worker** polls that queue, claims one job atomically, performs
   it, and records either the result or an error.

The queue is a shared SQLite database, so the example uses only Python's standard
library and needs no package installation.

## Run it

Requires Python 3.10 or newer. Open two terminals in this directory.

Terminal 1 — start the API:

```bash
python3 api.py
```

Terminal 2 — start the worker:

```bash
python3 worker.py
```

Submit a job:

```bash
curl -i http://127.0.0.1:8000/jobs \
  -H 'Content-Type: application/json' \
  -d '{"task":"uppercase","payload":{"text":"hello background worker"}}'
```

The response is `202 Accepted` and contains an `id`. Check it after the worker
has had a moment to process it:

```bash
curl http://127.0.0.1:8000/jobs/JOB_ID
```

The final response includes `"status": "completed"` and:

```json
{"result": {"text": "HELLO BACKGROUND WORKER"}}
```

You can also list jobs with `GET /jobs` and check the API with `GET /health`.

## Supported tasks

| Task | Input payload | Result |
| --- | --- | --- |
| `uppercase` | `{"text":"Hello"}` | `{"text":"HELLO"}` |
| `reverse` | `{"text":"abc"}` | `{"text":"cba"}` |
| `word_count` | `{"text":"one two"}` | `{"count":2}` |

## Important behavior

- **Durability:** queued jobs survive API and worker restarts.
- **Atomic claims:** the write transaction prevents two workers from taking the
  same job. You can run more than one `worker.py` process.
- **Retries:** failures return to the queue until `max_attempts` is reached.
  Clients can set `max_attempts` from 1 to 10 when creating a job.
- **Crash recovery:** a job held longer than the worker lease is assumed abandoned
  and is retried. Configure the lease with `JOB_LEASE_SECONDS`.
- **Separation:** the API never performs the task. It responds quickly after
  enqueueing, while the worker handles execution independently.

For a production system, replace SQLite polling with a queue service such as
Redis, RabbitMQ, SQS, or a database queue designed for higher throughput.

## Configuration

| Environment variable | Default |
| --- | --- |
| `JOB_DATABASE` | `./data/jobs.db` |
| `JOB_API_HOST` | `127.0.0.1` |
| `JOB_API_PORT` | `8000` |
| `WORKER_POLL_SECONDS` | `0.5` |
| `JOB_LEASE_SECONDS` | `30` |

## Tests

```bash
python3 -m unittest discover -s tests -v
```


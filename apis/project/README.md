# Task API project

This small FastAPI service is the final exercise for the API learning path. It stores data in memory so you can focus on HTTP, contracts, validation, and errors.

## Setup

You need Python 3.10 or newer.

```bash
cd apis/project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
fastapi dev main.py
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Then open:

- API: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI description: http://127.0.0.1:8000/openapi.json

## Start by reading

Before running the service, inspect `main.py` and predict:

1. What will `GET /health` return?
2. What will `GET /tasks` return?
3. What fields does one task contain?
4. Where does the data live?
5. What happens to the data when the service restarts?

## Build next

Implement the TODO endpoints from the learning path:

- `POST /tasks`
- `GET /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

Use the generated `/docs` page to inspect the contract and test each endpoint.

## Constraints

- Keep storage in memory.
- Return JSON except for a successful `204 No Content`.
- Use `404` when a requested task does not exist.
- Let FastAPI validation show you what invalid input looks like.
- Record every surprising result in `../exercises.md`.

## Completion check

The project is complete when you can demonstrate every endpoint, one validation failure, one missing-resource failure, and explain the exact request and response for each.

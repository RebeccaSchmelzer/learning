from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Task API", version="0.1.0")


class TaskCreate(BaseModel):
    title: str


class Task(TaskCreate):
    id: int
    completed: bool = False


tasks: list[Task] = [
    Task(id=1, title="Trace an HTTP request"),
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return tasks


# TODO: Add POST /tasks and return 201 Created.
# TODO: Add GET /tasks/{task_id} and return 404 when it is missing.
# TODO: Add DELETE /tasks/{task_id} and return 204 No Content.

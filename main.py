from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

app = FastAPI(title="Task API", version="1.0")


# --- models -----------------------------------------------------------

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str

    # empty/whitespace titles slip past a plain `str` type check, so this
    # catches them explicitly instead of letting a blank task get created
    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v


# --- "database" ---------------------------------------------------------
# Simple in-memory storage for now (resets on server restart)

tasks: list[dict] = []
next_id: int = 1


def seed() -> None:
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Walk the dog", "done": False},
        {"id": 3, "title": "Write README", "done": True},
    ]
    next_id = 4


seed()


def find_task(task_id: int) -> Optional[dict]:
    return next((t for t in tasks if t["id"] == task_id), None)


# --- root & health --------------------------------------------------------

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


# --- read -------------------------------------------------------------

@app.get("/tasks")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    # optional filtering via query params, e.g. /tasks?done=true&search=milk
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        result = [t for t in result if search.lower() in t["title"].lower()]
    return result


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# --- create -------------------------------------------------------------

@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    global next_id
    task = {"id": next_id, "title": payload.title, "done": False}
    tasks.append(task)
    next_id += 1
    return task


# --- update & delete ------------------------------------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if payload.title is None and payload.done is None:
        # nothing to update - treat as a bad request rather than a silent no-op
        raise HTTPException(status_code=400, detail="Provide at least title or done")
    if payload.title is not None:
        task["title"] = payload.title
    if payload.done is not None:
        task["done"] = payload.done
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return None


# --- extras: stats & reset ------------------------------------------------
# Helper endpoints for debugging and metrics

@app.get("/stats")
def stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/reset")
def reset():
    seed()
    return {"status": "reset", "tasks": tasks}


# --- error handling ------------------------------------------------------
# Override FastAPI's default 422 validation response format with a standard 400 / error shape

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]
    field = ".".join(str(p) for p in first_error["loc"] if p != "body")
    return JSONResponse(
        status_code=400,
        content={"error": f"{field}: {first_error['msg']}"},
    )

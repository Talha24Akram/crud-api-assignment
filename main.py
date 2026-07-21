from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0")

# --- models -----------------------------------------------------------

class TaskCreate(BaseModel):
    title: str

# --- "database" ---------------------------------------------------------
# just a list in memory, per the assignment - no db until next week

tasks: list[dict] = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Write README", "done": True},
]
next_id: int = 4

# --- error handling ------------------------------------------------------
# FastAPI defaults to {"detail": ...} and 422 on validation errors - the
# assignment wants {"error": ...} and 400, so both get overridden here

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

# --- root & health --------------------------------------------------------

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- read -------------------------------------------------------------

@app.get("/tasks")
def list_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
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

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

tasks = {
    1: {"id": 1, "title": "Buy milk", "done": False},
    2: {"id": 2, "title": "Walk the dog", "done": False},
    3: {"id": 3, "title": "Write README", "done": True},
}
next_id = 4


class Task(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return list(tasks.values())


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return tasks[task_id]


@app.post("/tasks", status_code=201)
def create_task(task: Task):
    global next_id
    new_task = {"id": next_id, "title": task.title, "done": task.done}
    tasks[next_id] = new_task
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    existing = tasks[task_id]
    if update.title is not None:
        existing["title"] = update.title
    if update.done is not None:
        existing["done"] = update.done
    return existing


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    del tasks[task_id]

# Task API

My submission for FlyRank's Backend Track, Week 2 (Assignment A1) — a small CRUD API for a
to-do list, built with FastAPI.

## What this is

Five endpoints, full CRUD on a list of tasks: create one, read them, update them, delete them.
No database — everything lives in a plain Python list in memory, which means restarting the
server wipes it back to the three seed tasks. More on that at the bottom.

## Running it

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python -m uvicorn main:app --port 8000
```

Once it's up, http://localhost:8000/docs gets you Swagger UI where you can click through every
endpoint without touching curl. I mostly used curl anyway out of habit, but Swagger's genuinely
nice for a quick sanity check.

## Endpoints

| Method | Path          | What it does                              | Success | Errors                        |
|--------|---------------|--------------------------------------------|---------|--------------------------------|
| GET    | `/`           | API info                                   | 200     | —                              |
| GET    | `/health`     | Health check                               | 200     | —                              |
| GET    | `/tasks`      | List tasks (`?done=` and `?search=` filter them) | 200 | —                        |
| GET    | `/tasks/{id}` | Get one task                               | 200     | 404 if it doesn't exist        |
| POST   | `/tasks`      | Create a task, body `{"title": "..."}`     | 201     | 400 if title's missing/blank   |
| PUT    | `/tasks/{id}` | Update `title` and/or `done`               | 200     | 400 empty body, 404 unknown id |
| DELETE | `/tasks/{id}` | Delete a task                              | 204     | 404 if it doesn't exist        |
| GET    | `/stats`      | `{"total", "done", "open"}` counts         | 200     | —                              |
| POST   | `/reset`      | Puts the 3 seed tasks back                 | 200     | —                              |

(`/stats` and `/reset` weren't required, just seemed like fun extras once the core five were
working.)

## One example

```
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

![Swagger UI screenshot](swagger-screenshot.png)

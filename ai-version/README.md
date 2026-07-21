# ai-version

Second implementation of the same Task API, generated from `prompt.txt` (Stage 7, the AI
rematch). Kept separate from the hand-built `main.py` in the repo root — this folder is not
touched by the main app.

Run it the same way, on a different port:
```
venv\Scripts\python -m uvicorn ai-version.main:app --port 8001 --app-dir .
```

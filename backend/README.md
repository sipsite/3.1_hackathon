# Backend (FastAPI)

## Environment variables (use on server, no .env file)

Set one of:

```bash
export GEMINI_API_KEY=your_key
# or
export OPENAI_API_KEY=your_key
```

Used for: poster image, brief, summary, comments, chat. Data is in `data.json` (no DB).

## Run on server

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ensure `frontend/dist` exists (from repo root: `cd frontend && npm run build`) so the app can serve the static site at `/`.

## Admin endpoints (manual trigger)

- `POST /api/admin/sync-papers?category=cs.LG&max_results=10` — fetch papers from arXiv into `data.json`.
- `POST /api/admin/generate-for-paper/{paper_id}` — generate poster URL, brief, summary, and persona comments for that paper; write to `data.json`.

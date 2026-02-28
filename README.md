# Paper Feed — Xiaohongshu-style research paper feed

English-only UI. Papers from arXiv, AI-generated poster/summary/comments and in-post chatbot. Data in `backend/data.json` (no external DB). No Docker, no Nginx: single uvicorn process serves frontend + API.

---

## Run on cloud server (EC2)

Do **not** run install/build locally if you only deploy on the server. On the **cloud server**:

1. **Clone and install**
   ```bash
   git clone <your-repo> && cd code
   export GEMINI_API_KEY=your_key   # or OPENAI_API_KEY
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install && npm run build
   ```

2. **Start the app**
   ```bash
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   One process serves the site at `http://<server-ip>:8000` (frontend at `/`, API at `/api`). Use `export GEMINI_API_KEY=...` (or `OPENAI_API_KEY`) in the same shell or via systemd `Environment=`.

3. **Seed data and generate content**
   - Sync papers from arXiv: `POST /api/admin/sync-papers?category=cs.LG&max_results=10`
   - Generate poster + brief + summary + comments for a paper: `POST /api/admin/generate-for-paper/{paper_id}`

Example with curl (on the server or from your machine if port open):
```bash
curl -X POST "http://localhost:8000/api/admin/sync-papers?max_results=5"
curl -X POST "http://localhost:8000/api/admin/generate-for-paper/2401.00001"
```

---

## Run locally (optional)

- Terminal 1: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
- Terminal 2: `cd frontend && npm install && npm run dev`
- Open http://localhost:5173 (Vite dev); or build frontend and open http://localhost:8000

Set `GEMINI_API_KEY` or `OPENAI_API_KEY` in the environment for AI features.

---

## Project layout

- `frontend/` — React (Vite), two-column feed, post detail, chat float. English only.
- `backend/` — FastAPI, `data.json` store, arXiv fetch, LLM (brief/summary/comments/chat), image poster. Config via `app/config.py` (env only).

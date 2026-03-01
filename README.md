# PaperDaily

A social media-style feed for research papers

## A. Problem & Solution

Research papers are information-dense and hard to scan. Abstract and PDFs alone don’t give a quick, intuitive sense of what a paper is about. This project offers a **more multimodal way to see papers**: a visual feed with AI-generated posters, short briefs, structured summaries, persona comments, and an in-article chatbot—so you can grasp and explore papers without reading the full text first.

---

## B. Functions

- **Feed** — Two-column, card-based feed of recent papers 
- **Paper detail** — Full post: poster, brief, bullet summary, full summary, abstract, and comments.
- **AI poster** — generated from full-text summary.
- **Persona comments** — Multiple AI-generated comments for quick, varied perspectives.
- **In-post chat** — Chatbot tied to the current paper; answers are grounded in the paper’s full summary.
- **Real-time Updates** — Built-in scheduled tasks (with configurable intervals) automatically pull new papers from arXiv and generate posters, summaries, and comments without manual intervention.
---

## C. Core Technology

- **Frontend** — React 18, Vite 5, React Router; features a single-page two-column feed, article detail pages, and a floating chat component.
- **Backend** — FastAPI; a single uvicorn process serves both the REST API and the frontend static assets (mounted from `frontend/dist`).
- **Data** — No external database; `backend/data.json` stores paper lists, summaries, and comments; all read/write operations are unified via `store.load/save`.
- **Paper Source** — arXiv API (RSS/Atom) fetches latest papers; PDFs are pulled with `httpx` and text is extracted using `PyMuPDF`.
- **LLM** — Supports Gemini and OpenAI; handles briefs, summaries, persona comments, poster prompts, and chat responses via a unified `llm` module.
- **Image Generation** — Posters are generated using the Gemini Image API based on LLM-synthesized prompts.
- **Scheduled Tasks** — APScheduler handles background sync and generation based on the `SYNC_INTERVAL_MINUTES` environment variable.
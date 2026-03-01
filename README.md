# PaperDaily

A social media-style feed for research papers

## A. Problem & Solution

Research papers are information-dense and hard to scan. Abstract and PDFs alone don’t give a quick, intuitive sense of what a paper is about. This project offers a **more multimodal way to see papers**: a visual feed with AI-generated posters, short briefs, structured summaries, persona comments, and an in-article chatbot—so you can grasp and explore papers without reading the full text first.

---

## B. Functions

- **Feed** — Two-column, card-based feed of recent papers (title, poster, one-line brief, comment count).
- **Paper detail** — Full post: poster, brief, bullet summary, full summary (from PDF), abstract, and comments.
- **AI poster** — One image per paper, generated from title + abstract + full-text summary (academic infographic style, no text in image).
- **Brief & summaries** — One-sentence brief for the feed; short bullet summary and an optional ~1000-word full summary produced by an LLM that reads the paper body.
- **Persona comments** — Multiple AI-generated comments (reviewer, PhD student, engineer, skeptic, domain expert) for quick, varied perspectives.
- **In-post chat** — Chatbot tied to the current paper; answers are grounded in the paper’s full summary (or abstract/summary if no full summary).
- **arXiv sync** — Pull recent papers from arXiv by category (e.g. cs.LG); optionally auto-generate poster, brief, summary, and comments for new papers.
- **Scheduled sync** — Optional in-process scheduler to run sync (e.g. every N minutes) with auto_generate, so the feed updates without manual triggers.

---

## C. Feature Highlights

- **Real-time Updates** — Built-in scheduled tasks (with configurable intervals) automatically pull new papers from arXiv and generate posters, summaries, and comments without manual intervention.
- **Full-text Summarization** — A single LLM reads the PDF body (first several pages) to generate a ~1,000-word structured summary. Briefs, summaries, comments, and poster prompts are all derived from this to avoid redundant processing.
- **Multimodal Presentation** — Each paper includes an AI-generated poster, text brief/summary, multi-persona comments, and an interactive chat for rapid, multi-angle understanding.
- **Persona-based Comments** — Fixed personas (Reviewer, PhD student, Engineer, Skeptic, Domain Expert) generate short reviews to simulate a community discussion environment.
- **Conversational Understanding** — Features an in-post chatbot grounded in the paper's specific context, supporting follow-up questions and clarifications.
- **Lightweight Storage** — No independent database required; a single `data.json` file stores all paper metadata and generated content. Posters are saved as Data URLs or URLs for easy backup and migration.

---

## D. Core Technology

- **Frontend** — React 18, Vite 5, React Router; features a single-page two-column feed, article detail pages, and a floating chat component.
- **Backend** — FastAPI; a single uvicorn process serves both the REST API and the frontend static assets (mounted from `frontend/dist`).
- **Data** — No external database; `backend/data.json` stores paper lists, summaries, and comments; all read/write operations are unified via `store.load/save`.
- **Paper Source** — arXiv API (RSS/Atom) fetches latest papers; PDFs are pulled with `httpx` and text is extracted using `PyMuPDF`.
- **LLM** — Supports Gemini and OpenAI; handles briefs, summaries, persona comments, poster prompts, and chat responses via a unified `llm` module.
- **Image Generation** — Posters are generated using the Gemini Image API based on LLM-synthesized prompts.
- **Scheduled Tasks** — APScheduler handles background sync and generation based on the `SYNC_INTERVAL_MINUTES` environment variable.
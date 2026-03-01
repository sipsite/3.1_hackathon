import logging
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import papers, comments, chat, admin

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def _scheduled_sync():
    """Run sync-papers with max_results=3, auto_generate=True (same as your curl)."""
    from app.routers.admin import run_sync_papers
    try:
        out = run_sync_papers(category="cs.LG", max_results=3, auto_generate=True)
        logger.info("scheduled sync: added=%s total=%s", out["added"], out["total"])
    except Exception as e:
        logger.exception("scheduled sync failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    if settings.SYNC_INTERVAL_MINUTES > 0:
        from datetime import datetime, timedelta
        _scheduler = BackgroundScheduler()
        _scheduler.add_job(
            _scheduled_sync,
            "interval",
            minutes=settings.SYNC_INTERVAL_MINUTES,
            id="sync_papers",
        )
        _scheduler.add_job(
            _scheduled_sync,
            "date",
            run_date=datetime.utcnow() + timedelta(seconds=30),
            id="sync_papers_startup",
        )
        _scheduler.start()
        logger.info("scheduled sync started: every %s min", settings.SYNC_INTERVAL_MINUTES)
    yield
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None


app = FastAPI(title="Paper Feed API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(papers.router, prefix="/api", tags=["papers"])
app.include_router(comments.router, prefix="/api", tags=["comments"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(admin.router, prefix="/api", tags=["admin"])

# Serve frontend static files (after build: frontend/dist)
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    index_path = frontend_dist / "index.html"

    @app.get("/paper/{path:path}")
    def serve_paper_page(path: str):
        if index_path.exists():
            return FileResponse(str(index_path))
        raise HTTPException(status_code=404)

    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


@app.get("/api/health")
def health():
    return {"status": "ok"}

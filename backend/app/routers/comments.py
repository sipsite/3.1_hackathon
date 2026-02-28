from fastapi import APIRouter
from app.store import load

router = APIRouter()


@router.get("/papers/{paper_id}/comments")
def list_comments(paper_id: str):
    data = load()
    comments = [c for c in data["comments"] if c.get("paper_id") == paper_id]
    return {"comments": comments}

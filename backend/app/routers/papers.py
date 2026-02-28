from fastapi import APIRouter, HTTPException
from app.store import load

router = APIRouter()


@router.get("/papers")
def list_papers():
    data = load()
    papers = list(data["papers"])
    content_map = data.get("paper_content", {})
    comments_by_paper = {}
    for c in data.get("comments", []):
        pid = c.get("paper_id")
        if pid:
            comments_by_paper.setdefault(pid, []).append(c)
    for p in papers:
        pid = p.get("id")
        extra = content_map.get(pid, {})
        p["brief"] = extra.get("brief", "")
        p["poster_url"] = extra.get("poster_url", "")
        p["comments"] = comments_by_paper.get(pid, [])
    return {"papers": papers}


@router.get("/papers/{paper_id}")
def get_paper(paper_id: str):
    data = load()
    papers = {p["id"]: p for p in data["papers"]}
    if paper_id not in papers:
        raise HTTPException(status_code=404, detail="Paper not found")
    paper = papers[paper_id]
    content = data["paper_content"].get(paper_id, {})
    comments = [c for c in data["comments"] if c.get("paper_id") == paper_id]
    return {
        **paper,
        "brief": content.get("brief", ""),
        "summary": content.get("summary", ""),
        "poster_url": content.get("poster_url", ""),
        "comments": comments,
    }

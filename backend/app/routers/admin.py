"""Manual trigger: sync papers from arXiv, generate poster/summary/comments for a paper."""
from fastapi import APIRouter, HTTPException
from app.store import load, save
from app.services import arxiv as arxiv_svc
from app.services import image_gen
from app.services import llm
from app.services import pdf_extract

router = APIRouter()


@router.post("/admin/sync-papers")
def sync_papers(category: str = "cs.LG", max_results: int = 10):
    data = load()
    existing_ids = {p["id"] for p in data["papers"]}
    new_papers = arxiv_svc.fetch_recent(category=category, max_results=max_results)
    added = 0
    for p in new_papers:
        if p["id"] not in existing_ids:
            data["papers"].append(p)
            existing_ids.add(p["id"])
            added += 1
    save(data)
    return {"added": added, "total": len(data["papers"])}


@router.post("/admin/generate-for-paper/{paper_id}")
def generate_for_paper(paper_id: str):
    data = load()
    papers = {p["id"]: p for p in data["papers"]}
    if paper_id not in papers:
        raise HTTPException(status_code=404, detail="Paper not found")
    paper = papers[paper_id]
    if paper_id not in data["paper_content"]:
        data["paper_content"][paper_id] = {}
    content = data["paper_content"][paper_id]

    if not content.get("brief"):
        content["brief"] = llm.generate_brief(paper["title"], paper["abstract"])
    if not content.get("summary"):
        content["summary"] = llm.generate_summary(paper["title"], paper["abstract"])
    if not content.get("poster_url"):
        pdf_url = paper.get("pdf_url") or f"https://arxiv.org/pdf/{paper_id}.pdf"
        pdf_bytes = arxiv_svc.fetch_pdf_bytes(pdf_url)
        if pdf_bytes:
            pdf_text = pdf_extract.extract_text(pdf_bytes)
            prompt = llm.generate_image_prompt(paper["title"], paper["abstract"], pdf_text)
            content["poster_url"] = image_gen.generate_poster_url_from_prompt(prompt) or ""
        else:
            content["poster_url"] = image_gen.generate_poster_url(paper["title"], paper["abstract"]) or ""

    comments_for_paper = [c for c in data["comments"] if c.get("paper_id") == paper_id]
    if not comments_for_paper:
        new_comments = llm.generate_comments(
            paper["title"], paper["abstract"], content.get("summary", "")
        )
        for c in new_comments:
            c["paper_id"] = paper_id
            data["comments"].append(c)

    save(data)
    return {"ok": True, "paper_id": paper_id}

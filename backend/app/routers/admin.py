"""Manual trigger: sync papers from arXiv, generate poster/summary/comments for a paper."""
from fastapi import APIRouter, HTTPException
from app.store import load, save
from app.services import arxiv as arxiv_svc
from app.services import image_gen
from app.services import llm
from app.services import pdf_extract

router = APIRouter()


# More pages for full-summary generation (one LLM reads this and writes ~1000-word summary)
FULL_SUMMARY_PDF_PAGES = 20


def _generate_content_for_paper(data: dict, paper_id: str) -> None:
    """Mutate data: generate full_summary first (from PDF), then brief, summary, poster, comments. Caller must save."""
    papers = {p["id"]: p for p in data["papers"]}
    if paper_id not in papers:
        return
    paper = papers[paper_id]
    if paper_id not in data["paper_content"]:
        data["paper_content"][paper_id] = {}
    content = data["paper_content"][paper_id]

    # One LLM reads full paper and produces full_summary; everyone else uses it
    if not content.get("full_summary"):
        pdf_url = paper.get("pdf_url") or f"https://arxiv.org/pdf/{paper_id}.pdf"
        pdf_bytes = arxiv_svc.fetch_pdf_bytes(pdf_url)
        if pdf_bytes:
            pdf_text = pdf_extract.extract_text(pdf_bytes, max_pages=FULL_SUMMARY_PDF_PAGES)
            content["full_summary"] = llm.generate_full_summary(
                paper["title"], paper["abstract"], pdf_text
            ) or ""

    full_summary = content.get("full_summary") or ""

    if not content.get("brief"):
        content["brief"] = llm.generate_brief(
            paper["title"], paper["abstract"], full_summary or None
        )
    if not content.get("summary"):
        content["summary"] = llm.generate_summary(
            paper["title"], paper["abstract"], full_summary or None
        )
    if not content.get("poster_url"):
        if full_summary:
            prompt = llm.generate_image_prompt(
                paper["title"], paper["abstract"], full_summary=full_summary
            )
        else:
            pdf_url = paper.get("pdf_url") or f"https://arxiv.org/pdf/{paper_id}.pdf"
            pdf_bytes = arxiv_svc.fetch_pdf_bytes(pdf_url)
            pdf_text = pdf_extract.extract_text(pdf_bytes) if pdf_bytes else ""
            prompt = llm.generate_image_prompt(
                paper["title"], paper["abstract"], pdf_text_snippet=pdf_text
            ) if pdf_text else None
        if prompt:
            content["poster_url"] = image_gen.generate_poster_url_from_prompt(prompt) or ""
        else:
            content["poster_url"] = image_gen.generate_poster_url(
                paper["title"], paper["abstract"]
            ) or ""

    comments_for_paper = [c for c in data["comments"] if c.get("paper_id") == paper_id]
    if not comments_for_paper:
        new_comments = llm.generate_comments(
            paper["title"],
            paper["abstract"],
            content.get("summary", ""),
            full_summary or None,
        )
        for c in new_comments:
            c["paper_id"] = paper_id
            data["comments"].append(c)


@router.post("/admin/sync-papers")
def sync_papers(category: str = "cs.LG", max_results: int = 10, auto_generate: bool = False):
    data = load()
    existing_ids = {p["id"] for p in data["papers"]}
    new_papers = arxiv_svc.fetch_recent(category=category, max_results=max_results)
    added_ids = []
    for p in new_papers:
        if p["id"] not in existing_ids:
            data["papers"].append(p)
            existing_ids.add(p["id"])
            added_ids.append(p["id"])
    if auto_generate and added_ids:
        for pid in added_ids:
            _generate_content_for_paper(data, pid)
    save(data)
    return {
        "added": len(added_ids),
        "total": len(data["papers"]),
        "generated": added_ids if auto_generate else [],
    }


@router.post("/admin/generate-for-paper/{paper_id}")
def generate_for_paper(paper_id: str):
    data = load()
    if paper_id not in {p["id"] for p in data["papers"]}:
        raise HTTPException(status_code=404, detail="Paper not found")
    _generate_content_for_paper(data, paper_id)
    save(data)
    return {"ok": True, "paper_id": paper_id}

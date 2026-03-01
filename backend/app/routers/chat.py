from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.store import load
from app.services.llm import chat_for_paper

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@router.post("/papers/{paper_id}/chat")
def post_chat(paper_id: str, body: ChatRequest):
    data = load()
    papers = {p["id"]: p for p in data["papers"]}
    if paper_id not in papers:
        raise HTTPException(status_code=404, detail="Paper not found")
    paper = papers[paper_id]
    content = data["paper_content"].get(paper_id, {})
    context = {
        "title": paper.get("title", ""),
        "abstract": paper.get("abstract", ""),
        "summary": content.get("summary", ""),
        "full_summary": content.get("full_summary", ""),
    }
    reply = chat_for_paper(context, [{"role": m.role, "content": m.content} for m in body.messages])
    return {"reply": reply}

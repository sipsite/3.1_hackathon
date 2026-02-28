"""Fetch papers from arXiv API. English only."""
import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

ARXIV_QUERY = "https://export.arxiv.org/api/query?"

def fetch_recent(category: str = "cs.LG", max_results: int = 20) -> List[Dict[str, Any]]:
    url = f"{ARXIV_QUERY}search_query=cat:{category}&sortBy=submittedDate&max_results={max_results}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    papers = []
    for entry in root.findall("atom:entry", ns):
        arxiv_id = _text(entry.find("atom:id", ns), "").split("/abs/")[-1].strip()
        title = _text(entry.find("atom:title", ns), "").strip().replace("\n", " ")
        summary = _text(entry.find("atom:summary", ns), "").strip().replace("\n", " ")
        authors = [a.text for a in entry.findall("atom:author/atom:name", ns) if a.text]
        link_pdf = ""
        for link in entry.findall("atom:link", ns):
            if link.get("title") == "pdf":
                link_pdf = link.get("href", "")
                break
        papers.append({
            "id": arxiv_id,
            "title": title,
            "abstract": summary,
            "authors": authors,
            "pdf_url": link_pdf or f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        })
    return papers


def fetch_pdf_bytes(pdf_url: str) -> bytes | None:
    """Fetch PDF for one paper by its pdf_url. Called only when generating poster (e.g. generate-for-paper). No disk write."""
    if not pdf_url:
        return None
    try:
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            resp = client.get(pdf_url)
            resp.raise_for_status()
            return resp.content
    except Exception:
        return None


def _text(el, default: str) -> str:
    if el is None:
        return default
    return (el.text or "") + "".join(ET.tostring(e, encoding="unicode", method="text") for e in el) or default

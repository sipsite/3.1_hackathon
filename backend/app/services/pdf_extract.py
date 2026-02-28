"""Extract plain text from PDF bytes via PyMuPDF. No file on disk."""
import fitz  # PyMuPDF


def extract_text(pdf_bytes: bytes, max_pages: int = 5) -> str:
    """Extract text from PDF bytes (first max_pages pages). Returns empty string on error."""
    if not pdf_bytes:
        return ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        parts = []
        for i in range(min(len(doc), max_pages)):
            page = doc.load_page(i)
            parts.append(page.get_text())
        doc.close()
        return "\n".join(parts).strip() or ""
    except Exception:
        return ""

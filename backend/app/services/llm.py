"""LLM: brief, summary, comments, chat. English only. Uses GEMINI_API_KEY or OPENAI_API_KEY."""
from app.config import settings
import random

# Token / length limits
DEFAULT_MAX_TOKENS = 10_000       # brief, summary, per-comment
IMAGE_PROMPT_MAX_TOKENS = 20_000
CHAT_MAX_TOKENS = 200_000

# Input truncation (characters)
ABSTRACT_SNIPPET_SHORT = 1_500    # brief + chat context
ABSTRACT_MAX_SUMMARY = 20_000
ABSTRACT_MAX_COMMENT = 800
PDF_SNIPPET_MAX = 30_000          # pdf excerpt + abstract for image prompt

# Personas for generated comments (English, hardcoded)
PERSONAS = [
    {"name": "Reviewer", "system_prompt": "You are a strict academic reviewer. Comment briefly on the paper in 1-2 sentences, noting one strength or one concern. Be concise and professional."},
    {"name": "PhD Student", "system_prompt": "You are a PhD student in ML. React to the paper in 1-2 sentences: what you found interesting or confusing. Casual but informed."},
    {"name": "Engineer", "system_prompt": "You are a practical engineer. In 1-2 sentences, say how this work might be applied or what you'd want to try. Plain English."},
    {"name": "Skeptic", "system_prompt": "You are a skeptic. In 1-2 sentences, raise one limitation or alternative explanation. Polite but critical."},
    {"name": "Domain Expert", "system_prompt": "You are a domain expert. In 1-2 sentences, place this work in context or compare to prior work. Authoritative tone."},
]


def _call_llm(system: str, user: str, max_tokens: int = 500) -> str:
    key = settings.llm_key
    if not key:
        return "(No API key set. Set GEMINI_API_KEY or OPENAI_API_KEY.)"
    if settings.GEMINI_API_KEY:
        return _gemini(system, user, key, max_tokens)
    return _openai(system, user, key, max_tokens)


def _gemini(system: str, user: str, key: str, max_tokens: int) -> str:
    try:
        import httpx
        r = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={key}",
            json={
                "contents": [{"parts": [{"text": f"{system}\n\n{user}"}]}],
                "generationConfig": {"maxOutputTokens": max_tokens},
            },
            timeout=60.0,
        )
        r.raise_for_status()
        out = r.json()
        for c in out.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if "text" in p:
                    return p["text"].strip()
    except Exception as e:
        return f"(Gemini error: {e})"
    return ""


def _openai(system: str, user: str, key: str, max_tokens: int) -> str:
    try:
        import httpx
        r = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "max_tokens": max_tokens,
            },
            timeout=60.0,
        )
        r.raise_for_status()
        out = r.json()
        return (out.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
    except Exception as e:
        return f"(OpenAI error: {e})"


def generate_brief(title: str, abstract: str) -> str:
    return _call_llm(
        "You write one short sentence (under 15 words) summarizing a research paper for a feed. English only. No quotes.",
        f"Title: {title}\nAbstract: {abstract[:ABSTRACT_SNIPPET_SHORT]}",
        max_tokens=DEFAULT_MAX_TOKENS,
    )


def generate_summary(title: str, abstract: str) -> str:
    return _call_llm(
        "You write a short bullet-point summary (3-5 bullets, one line each, short sentences) of the paper. English only. Plain text.",
        f"Title: {title}\nAbstract: {abstract[:ABSTRACT_MAX_SUMMARY]}",
        max_tokens=DEFAULT_MAX_TOKENS,
    )

prompt_options = ["Keep the response relatively short (avoid long essays), Use a natural, casual, conversational tone — like chatting, not a formal essay, Add personal opinions and feelings, Allow slight logical jumps or associative thinking, Include small personal anecdotes or examples (can be fictional but plausible)", 
"Keep the response relatively short (avoid long essays), Use a natural, casual, conversational tone — like chatting, not a formal essay, Use more colloquial and slightly imperfect phrasing, Occasionally use abbreviations (kinda, tbh, idk, etc.), Add some subjective judgments",
"Keep the response relatively short (avoid long essays), Use a natural, casual, conversational tone — like chatting, not a formal essay, Use richer and more varied descriptive modifiers, Avoid overly rigid structure or textbook-style organization, Let it feel like a real person thinking out loud"
]

def generate_comments(title: str, abstract: str, summary: str) -> list[dict]:
    comments = []
    text = f"Title: {title}\nSummary: {summary or abstract[:ABSTRACT_MAX_COMMENT]}"
    for persona in PERSONAS:

        reply = _call_llm(
            persona["system_prompt"] + " Avoid being overly helpful or structured. Use a casual, conversational tone. Use lowercase where appropriate, occasional abbreviations (like tbh, ngl, idk), and keep the sentences varying in length. Don't use 'As an AI' or perfect transition words like 'Furthermore' or 'In conclusion'. Output only the comment, no label.",
            text,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        comments.append({"persona": persona["name"], "text": reply})
    return comments


def generate_image_prompt(title: str, abstract: str, pdf_text_snippet: str) -> str:
    """Generate a single English prompt for an image model (academic poster, no text in image)."""
    snippet = (pdf_text_snippet or "")[:PDF_SNIPPET_MAX].strip()
    user = f"Title: {title}\nAbstract: {abstract[:PDF_SNIPPET_MAX]}\n\nExcerpt from paper (first pages):\n{snippet}"
    sys = (
        "You are a prompt writer for an image generation model. "
        "Given a research paper's title, abstract, and a short excerpt, output exactly one short English sentence (under 25 words) "
        "describing how to draw an academic poster-style image: professional academic infographic with a rigorous logical flowchart, blending precise scientific schematics with witty, minimalist hand-drawn illustrations and clever visual metaphors, clean vector lines, high-contrast academic color palette, organized hierarchy, sophisticated yet playful aesthetic, 4k resolution."
        "Output only the prompt, nothing else."
    )
    return _call_llm(sys, user, max_tokens=IMAGE_PROMPT_MAX_TOKENS).strip() or "Academic poster style image for a research paper, modern layout, no text in image."


def chat_for_paper(context: dict, messages: list[dict]) -> str:
    sys = (
        "You are a helpful assistant discussing a research paper. Answer in English only, briefly and accurately based on the given paper context."
    )
    ctx_text = f"Paper title: {context.get('title', '')}\nAbstract: {context.get('abstract', '')[:ABSTRACT_SNIPPET_SHORT]}\nSummary: {context.get('summary', '')}"
    user_msgs = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-10:])
    return _call_llm(sys, f"Context:\n{ctx_text}\n\nConversation:\n{user_msgs}", max_tokens=CHAT_MAX_TOKENS)

"""Poster image URL via Gemini/Imagen or placeholder. Saves URL to data.json via caller."""
import httpx
from app.config import settings


def generate_poster_url(title: str, abstract: str) -> str | None:
    """Return a poster image URL (or placeholder). Caller writes to data.json."""
    key = settings.GEMINI_API_KEY or settings.OPENAI_API_KEY
    if not key:
        return None
    prompt = f"Academic poster style image for a research paper. Title: {title}. Minimal text, modern layout, scientific. No text in image."
    if settings.GEMINI_API_KEY:
        return _gemini_image(key, prompt)
    return _openai_image(key, prompt)


def _gemini_image(key: str, prompt: str) -> str | None:
    try:
        r = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
            },
            timeout=60.0,
        )
        if r.status_code != 200:
            return None
        out = r.json()
        for c in out.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if "inlineData" in p and p["inlineData"].get("mimeType", "").startswith("image/"):
                    import base64
                    b64 = p["inlineData"].get("data")
                    if b64:
                        return f"data:{p['inlineData'].get('mimeType', 'image/png')};base64,{b64}"
    except Exception:
        pass
    return None


def _openai_image(key: str, prompt: str) -> str | None:
    try:
        r = httpx.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "dall-e-3", "prompt": prompt[:1000], "n": 1, "size": "1024x1024"},
            timeout=60.0,
        )
        if r.status_code != 200:
            return None
        out = r.json()
        for d in out.get("data", []):
            if d.get("url"):
                return d["url"]
    except Exception:
        pass
    return None

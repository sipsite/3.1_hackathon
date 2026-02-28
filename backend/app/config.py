"""Config from environment only. No pydantic-settings."""
import os

def get(key: str, default: str = "") -> str:
    return os.getenv(key, default)

class Settings:
    GEMINI_API_KEY: str = get("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = get("OPENAI_API_KEY", "")

    @property
    def llm_key(self) -> str:
        return self.GEMINI_API_KEY or self.OPENAI_API_KEY

settings = Settings()

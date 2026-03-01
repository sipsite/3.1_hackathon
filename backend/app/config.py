"""Config from environment only. No pydantic-settings."""
import os

def get(key: str, default: str = "") -> str:
    return os.getenv(key, default)

class Settings:
    GEMINI_API_KEY: str = get("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = get("OPENAI_API_KEY", "")

    # Scheduled sync: interval in minutes, 0 = disabled
    SYNC_INTERVAL_MINUTES: int = int(get("SYNC_INTERVAL_MINUTES", "60") or "0")

    @property
    def llm_key(self) -> str:
        return self.GEMINI_API_KEY or self.OPENAI_API_KEY

settings = Settings()

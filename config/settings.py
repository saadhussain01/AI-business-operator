"""
config/settings.py — Central configuration for AI Business Operator
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    # App
    APP_NAME: str = os.getenv("APP_NAME", "AI Business Operator")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # LLM Provider — default is Gemini (free)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")

    # Google Gemini — uses new google-genai SDK
    # Model names for the new SDK use format: "gemini-2.0-flash" (no version suffix)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # Anthropic Claude (optional fallback)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

    # Search
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", 8))
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"

    # Vector Store / Memory
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", str(BASE_DIR / "memory" / "vector_store"))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    ENABLE_MEMORY: bool = os.getenv("ENABLE_MEMORY", "true").lower() == "true"

    # Agents
    MAX_TOKENS_PER_AGENT: int = int(os.getenv("MAX_TOKENS_PER_AGENT", 2000))
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", 60))

    # Reports
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", str(BASE_DIR / "reports"))

    def get_llm_key(self) -> str:
        if self.LLM_PROVIDER == "anthropic":
            return self.ANTHROPIC_API_KEY
        return self.GEMINI_API_KEY

    def get_model(self) -> str:
        if self.LLM_PROVIDER == "anthropic":
            return self.ANTHROPIC_MODEL
        return self.GEMINI_MODEL


settings = Settings()

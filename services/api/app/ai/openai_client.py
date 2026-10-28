from openai import AsyncOpenAI

from app.core.config import get_settings


def client() -> AsyncOpenAI | None:
    settings = get_settings()
    key = settings.openai_api_key.get_secret_value()
    return AsyncOpenAI(api_key=key, timeout=25, max_retries=1) if key else None

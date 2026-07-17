import logging
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings

logger = logging.getLogger("sedap.llm")

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_SYSTEM_MESSAGE = (
    "You are SEDAP, a precise document analysis assistant. Answer the user's "
    "question using ONLY the provided context passages. If the context does not "
    "contain the answer, say so explicitly."
)


class LLMService(ABC):
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        system_message: str | None = None,
        max_tokens: int = 500,
    ) -> str:
        ...


class MockLLMProvider(LLMService):
    async def generate_response(
        self,
        prompt: str,
        system_message: str | None = None,
        max_tokens: int = 500,
    ) -> str:
        snippet = prompt[:60]
        summary = " ".join(prompt.split())[:120]
        return (
            "[Mock LLM Response] Received Prompt: "
            f"{snippet}... "
            f"[Summary] {summary}"
        )


class OpenAILLMProvider(LLMService):
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.LLM_MODEL
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

    async def generate_response(
        self,
        prompt: str,
        system_message: str | None = None,
        max_tokens: int = 500,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        messages = [
            {"role": "system", "content": system_message or DEFAULT_SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OPENAI_CHAT_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return str(data["choices"][0]["message"]["content"])


def get_llm_service() -> LLMService:
    provider = settings.LLM_PROVIDER
    if provider == "local":
        return MockLLMProvider()
    if provider == "openai":
        return OpenAILLMProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider!r} (supported: 'local', 'openai')")

import logging
import time
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

logger = logging.getLogger("sedap.memory")


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    timestamp: float = Field(default_factory=time.time)


class BaseMemoryStore(ABC):
    @abstractmethod
    async def get_history(self, session_id: str) -> list[ChatMessage]:
        ...

    @abstractmethod
    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        ...


class InMemoryMemoryStore(BaseMemoryStore):
    def __init__(self) -> None:
        self._sessions: dict[str, list[ChatMessage]] = {}

    async def get_history(self, session_id: str) -> list[ChatMessage]:
        return list(self._sessions.get(session_id, []))

    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        self._sessions.setdefault(session_id, []).append(message)
        logger.info("session %s now has %d messages", session_id, len(self._sessions[session_id]))


def get_memory_store() -> BaseMemoryStore:
    return InMemoryMemoryStore()

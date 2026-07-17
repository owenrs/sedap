import logging
import re
from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.entities import ExtractedEntities

logger = logging.getLogger("sedap.extractor")

_DATE_PATTERN = re.compile(
    r"\b("
    r"\d{4}-\d{2}-\d{2}"
    r"|\d{1,2}/\d{1,2}/\d{2,4}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
    r")\b"
)
_PROPER_NOUN = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")
_ORG_LEAD = {"Project", "API"}
_STOPWORDS = {"The", "On", "A", "An", "In", "At", "To", "Of", "For", "And", "With"}


class EntityExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> ExtractedEntities:
        ...


class RuleBasedExtractor(EntityExtractor):
    def __init__(self, keywords: list[str] | None = None) -> None:
        self._keywords = [k.strip() for k in (keywords or []) if k.strip()]

    def extract(self, text: str) -> ExtractedEntities:
        found_keywords = [
            kw for kw in self._keywords if kw and re.search(rf"\b{re.escape(kw)}\b", text)
        ]

        people: list[str] = []
        organizations: list[str] = []
        for match in _PROPER_NOUN.findall(text):
            token = match.strip()
            lead = token.split()[0]
            if lead in _ORG_LEAD:
                organizations.append(token)
            elif lead in _STOPWORDS:
                continue
            elif token.split()[0] in self._keywords:
                continue
            else:
                people.append(token)
        people = _dedupe(people)
        organizations = _dedupe(organizations)

        dates = _dedupe(_DATE_PATTERN.findall(text))

        return ExtractedEntities(
            keywords=_dedupe(found_keywords),
            organizations=organizations,
            people=people,
            dates=dates,
        )


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def get_extractor() -> EntityExtractor:
    provider = settings.ENTITY_EXTRACTOR
    if provider == "rule":
        keywords = [k for k in settings.ENTITY_KEYWORDS.split(",") if k.strip()]
        return RuleBasedExtractor(keywords=keywords)
    raise ValueError(f"Unsupported ENTITY_EXTRACTOR: {provider!r} (supported: 'rule')")

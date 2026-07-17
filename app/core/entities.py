from pydantic import BaseModel, Field


class ExtractedEntities(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.keywords or self.organizations or self.people or self.dates)

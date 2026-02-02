"""Data models for the research agent."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SearchResultType(str, Enum):
    """Type of search result."""

    WEB = "web"
    NEWS = "news"


class SearchResult(BaseModel):
    """A single search result from web search."""

    title: str
    url: str
    snippet: str
    source: str | None = None


class WebPageContent(BaseModel):
    """Content extracted from a web page."""

    url: str
    title: str
    content: str
    fetch_timestamp: datetime = Field(default_factory=datetime.now)


class ResearchQuery(BaseModel):
    """A research query to investigate."""

    topic: str = Field(..., description="The main topic to research")
    focus_areas: list[str] = Field(
        default_factory=list, description="Specific areas to focus on"
    )
    max_sources: int = Field(default=10, description="Maximum number of sources to gather")
    depth: str = Field(
        default="standard",
        description="Research depth: 'quick', 'standard', or 'deep'",
    )


class Source(BaseModel):
    """A source used in the research."""

    title: str
    url: str
    relevance: str | None = None


class Section(BaseModel):
    """A section of the research report."""

    heading: str
    content: str


class ResearchReport(BaseModel):
    """A completed research report."""

    title: str
    query: ResearchQuery
    summary: str
    sections: list[Section]
    sources: list[Source]
    generated_at: datetime = Field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """Convert the report to markdown format."""
        lines = [
            f"# {self.title}",
            "",
            f"*Generated on {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Summary",
            "",
            self.summary,
            "",
        ]

        for section in self.sections:
            lines.extend([f"## {section.heading}", "", section.content, ""])

        lines.extend(["## Sources", ""])
        for i, source in enumerate(self.sources, 1):
            lines.append(f"{i}. [{source.title}]({source.url})")
            if source.relevance:
                lines.append(f"   - *{source.relevance}*")

        lines.append("")
        return "\n".join(lines)

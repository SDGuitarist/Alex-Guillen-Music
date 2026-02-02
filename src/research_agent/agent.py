"""Core research agent implementation using Claude."""

import json
import os
from datetime import datetime
from pathlib import Path

import anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from research_agent.models import (
    ResearchQuery,
    ResearchReport,
    SearchResult,
    Section,
    Source,
    WebPageContent,
)
from research_agent.search import WebSearcher

console = Console()


class ResearchAgent:
    """AI-powered research agent using Claude for analysis and synthesis."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        reports_dir: str | Path | None = None,
    ):
        """Initialize the research agent.

        Args:
            api_key: Anthropic API key. Defaults to ANTHROPIC_API_KEY env var.
            model: Claude model to use. Defaults to claude-sonnet-4-20250514.
            reports_dir: Directory to save reports. Defaults to ./reports.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.reports_dir = Path(reports_dir or os.getenv("REPORTS_DIR", "./reports"))
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.searcher = WebSearcher()

    def _generate_search_queries(self, query: ResearchQuery) -> list[str]:
        """Use Claude to generate effective search queries.

        Args:
            query: The research query.

        Returns:
            List of search queries to execute.
        """
        prompt = f"""Generate search queries for researching the following topic.

Topic: {query.topic}
Focus areas: {', '.join(query.focus_areas) if query.focus_areas else 'General overview'}
Depth: {query.depth}

Generate {3 if query.depth == 'quick' else 5 if query.depth == 'standard' else 8} diverse search queries that will help gather comprehensive information on this topic. Each query should target different aspects or perspectives.

Return ONLY a JSON array of search query strings, nothing else. Example:
["query 1", "query 2", "query 3"]"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            content = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            queries = json.loads(content)
            return queries if isinstance(queries, list) else [query.topic]
        except (json.JSONDecodeError, IndexError):
            return [query.topic]

    def _analyze_sources(
        self,
        query: ResearchQuery,
        search_results: list[SearchResult],
        page_contents: list[WebPageContent],
    ) -> str:
        """Use Claude to analyze gathered sources and synthesize information.

        Args:
            query: The original research query.
            search_results: Search results from web search.
            page_contents: Full content from fetched pages.

        Returns:
            Synthesized analysis as JSON string.
        """
        # Build context from sources
        sources_context = []
        for content in page_contents:
            sources_context.append(
                f"### Source: {content.title}\nURL: {content.url}\n\n{content.content}\n"
            )

        # Add snippets from search results not fully fetched
        fetched_urls = {c.url for c in page_contents}
        for result in search_results:
            if result.url not in fetched_urls:
                sources_context.append(
                    f"### Source: {result.title}\nURL: {result.url}\n\n{result.snippet}\n"
                )

        sources_text = "\n---\n".join(sources_context[:15])  # Limit sources

        prompt = f"""You are a research analyst. Analyze the following sources and create a comprehensive research report.

## Research Topic
{query.topic}

## Focus Areas
{', '.join(query.focus_areas) if query.focus_areas else 'General overview'}

## Sources
{sources_text}

## Instructions
Create a structured research report with:
1. A clear, descriptive title
2. An executive summary (2-3 paragraphs)
3. Multiple sections covering different aspects of the topic
4. Key findings and insights

Return your analysis as a JSON object with this exact structure:
{{
    "title": "Report title",
    "summary": "Executive summary text",
    "sections": [
        {{"heading": "Section 1 Title", "content": "Section 1 content..."}},
        {{"heading": "Section 2 Title", "content": "Section 2 content..."}}
    ],
    "source_relevance": [
        {{"url": "source url", "relevance": "Brief note on relevance"}}
    ]
}}

Make the content informative, well-organized, and cite specific findings from the sources."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    async def research(self, query: ResearchQuery) -> ResearchReport:
        """Conduct research on a topic and generate a report.

        Args:
            query: The research query specification.

        Returns:
            A completed research report.
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Step 1: Generate search queries
            task = progress.add_task("Generating search queries...", total=None)
            search_queries = self._generate_search_queries(query)
            progress.update(task, description="Generated search queries")
            console.print(f"  [dim]Created {len(search_queries)} search queries[/dim]")

            # Step 2: Execute searches
            progress.update(task, description="Searching the web...")
            all_results: list[SearchResult] = []
            seen_urls: set[str] = set()

            for sq in search_queries:
                results = self.searcher.search(sq, max_results=query.max_sources // len(search_queries) + 1)
                for r in results:
                    if r.url not in seen_urls:
                        all_results.append(r)
                        seen_urls.add(r.url)

            # Limit total results
            all_results = all_results[: query.max_sources]
            console.print(f"  [dim]Found {len(all_results)} unique sources[/dim]")

            # Step 3: Fetch page content
            progress.update(task, description="Fetching page content...")
            async with self.searcher:
                urls_to_fetch = [r.url for r in all_results]
                # Fetch more pages for deeper research
                max_pages = 3 if query.depth == "quick" else 6 if query.depth == "standard" else 10
                page_contents = await self.searcher.fetch_multiple_pages(
                    urls_to_fetch[:max_pages]
                )
            console.print(f"  [dim]Successfully fetched {len(page_contents)} pages[/dim]")

            # Step 4: Analyze and synthesize
            progress.update(task, description="Analyzing sources with Claude...")
            analysis_json = self._analyze_sources(query, all_results, page_contents)

            # Step 5: Parse and build report
            progress.update(task, description="Building report...")
            try:
                # Handle potential markdown code blocks
                content = analysis_json.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0]
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                analysis = {
                    "title": f"Research Report: {query.topic}",
                    "summary": analysis_json[:1000],
                    "sections": [{"heading": "Analysis", "content": analysis_json}],
                    "source_relevance": [],
                }

            # Build sources list
            relevance_map = {
                sr.get("url", ""): sr.get("relevance", "")
                for sr in analysis.get("source_relevance", [])
            }

            sources = []
            for result in all_results:
                sources.append(
                    Source(
                        title=result.title,
                        url=result.url,
                        relevance=relevance_map.get(result.url),
                    )
                )

            report = ResearchReport(
                title=analysis.get("title", f"Research Report: {query.topic}"),
                query=query,
                summary=analysis.get("summary", ""),
                sections=[
                    Section(heading=s["heading"], content=s["content"])
                    for s in analysis.get("sections", [])
                ],
                sources=sources,
                generated_at=datetime.now(),
            )

            progress.update(task, description="[green]Research complete!")

        return report

    def save_report(self, report: ResearchReport, filename: str | None = None) -> Path:
        """Save a research report to a markdown file.

        Args:
            report: The report to save.
            filename: Optional filename. Defaults to timestamp-based name.

        Returns:
            Path to the saved report.
        """
        if filename is None:
            timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c if c.isalnum() else "_" for c in report.title[:50])
            filename = f"{timestamp}_{safe_topic}.md"

        filepath = self.reports_dir / filename
        filepath.write_text(report.to_markdown())
        return filepath

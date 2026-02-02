"""Web search and content fetching functionality."""

import asyncio
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from rich.console import Console

from research_agent.models import SearchResult, WebPageContent

console = Console()


class WebSearcher:
    """Handles web searching and content fetching."""

    def __init__(self, timeout: float = 10.0):
        """Initialize the web searcher.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Perform a web search using DuckDuckGo.

        Args:
            query: The search query.
            max_results: Maximum number of results to return.

        Returns:
            List of search results.
        """
        results = []
        try:
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                for result in search_results:
                    results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            url=result.get("href", ""),
                            snippet=result.get("body", ""),
                            source=result.get("source"),
                        )
                    )
        except Exception as e:
            console.print(f"[yellow]Search warning: {e}[/yellow]")

        return results

    def search_news(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search for news articles.

        Args:
            query: The search query.
            max_results: Maximum number of results to return.

        Returns:
            List of news search results.
        """
        results = []
        try:
            with DDGS() as ddgs:
                news_results = ddgs.news(query, max_results=max_results)
                for result in news_results:
                    results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            url=result.get("url", ""),
                            snippet=result.get("body", ""),
                            source=result.get("source"),
                        )
                    )
        except Exception as e:
            console.print(f"[yellow]News search warning: {e}[/yellow]")

        return results

    async def fetch_page_content(self, url: str) -> WebPageContent | None:
        """Fetch and extract content from a web page.

        Args:
            url: The URL to fetch.

        Returns:
            Extracted page content or None if fetch failed.
        """
        if not self._client:
            raise RuntimeError("WebSearcher must be used as async context manager")

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string or ""

            # Extract main content
            # Try to find main content areas
            main_content = None
            for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            if main_content:
                text = main_content.get_text(separator="\n", strip=True)
            else:
                text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

            # Clean up the text
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            content = "\n".join(lines)

            # Limit content length
            max_chars = 8000
            if len(content) > max_chars:
                content = content[:max_chars] + "..."

            return WebPageContent(
                url=url,
                title=title.strip(),
                content=content,
                fetch_timestamp=datetime.now(),
            )

        except httpx.HTTPStatusError as e:
            console.print(f"[yellow]HTTP error fetching {url}: {e.response.status_code}[/yellow]")
        except httpx.RequestError as e:
            console.print(f"[yellow]Request error fetching {url}: {e}[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Error fetching {url}: {e}[/yellow]")

        return None

    async def fetch_multiple_pages(
        self, urls: list[str], max_concurrent: int = 5
    ) -> list[WebPageContent]:
        """Fetch content from multiple URLs concurrently.

        Args:
            urls: List of URLs to fetch.
            max_concurrent: Maximum concurrent requests.

        Returns:
            List of successfully fetched page contents.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(url: str) -> WebPageContent | None:
            async with semaphore:
                return await self.fetch_page_content(url)

        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks)

        return [r for r in results if r is not None]

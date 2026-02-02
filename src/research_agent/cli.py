"""Command-line interface for the research agent."""

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from research_agent.agent import ResearchAgent
from research_agent.models import ResearchQuery

console = Console()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-powered research agent that searches the web and generates reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  research-agent "artificial intelligence trends 2024"
  research-agent "climate change solutions" --depth deep --focus "renewable energy,carbon capture"
  research-agent "Python web frameworks" --max-sources 15 --output ./my-reports
        """,
    )

    parser.add_argument(
        "topic",
        help="The topic to research",
    )

    parser.add_argument(
        "--focus",
        "-f",
        help="Comma-separated list of specific areas to focus on",
        default="",
    )

    parser.add_argument(
        "--depth",
        "-d",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Research depth: quick (3 queries, 3 pages), standard (5 queries, 6 pages), or deep (8 queries, 10 pages)",
    )

    parser.add_argument(
        "--max-sources",
        "-m",
        type=int,
        default=10,
        help="Maximum number of sources to gather (default: 10)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Directory to save the report (default: ./reports)",
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save the report to a file, only print to console",
    )

    parser.add_argument(
        "--model",
        help="Claude model to use (default: claude-sonnet-4-20250514)",
    )

    parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file (default: .env in current directory)",
    )

    return parser.parse_args()


async def run_research(args: argparse.Namespace) -> int:
    """Run the research agent with the given arguments.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Load environment variables
    env_file = args.env_file or Path(".env")
    if env_file.exists():
        load_dotenv(env_file)

    # Parse focus areas
    focus_areas = [f.strip() for f in args.focus.split(",") if f.strip()]

    # Create research query
    query = ResearchQuery(
        topic=args.topic,
        focus_areas=focus_areas,
        max_sources=args.max_sources,
        depth=args.depth,
    )

    # Display research parameters
    console.print()
    console.print(
        Panel(
            f"[bold]Topic:[/bold] {query.topic}\n"
            f"[bold]Focus:[/bold] {', '.join(query.focus_areas) or 'General overview'}\n"
            f"[bold]Depth:[/bold] {query.depth}\n"
            f"[bold]Max sources:[/bold] {query.max_sources}",
            title="Research Parameters",
            border_style="blue",
        )
    )
    console.print()

    try:
        # Initialize agent
        agent = ResearchAgent(
            model=args.model,
            reports_dir=args.output,
        )

        # Run research
        report = await agent.research(query)

        console.print()

        # Save report if requested
        if not args.no_save:
            filepath = agent.save_report(report)
            console.print(f"[green]Report saved to:[/green] {filepath}")
            console.print()

        # Display report
        console.print(Panel(Markdown(report.to_markdown()), title="Research Report", border_style="green"))

        return 0

    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        return 1
    except Exception as e:
        console.print(f"[red]Error during research:[/red] {e}")
        if "--debug" in sys.argv:
            console.print_exception()
        return 1


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    try:
        exit_code = asyncio.run(run_research(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Research cancelled by user[/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    main()

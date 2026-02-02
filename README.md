# Research Agent

An AI-powered research agent that performs web searches and generates comprehensive markdown reports using Claude.

## Features

- **Web Search**: Automatically searches the web using DuckDuckGo for relevant sources
- **Content Extraction**: Fetches and parses web page content for analysis
- **AI Analysis**: Uses Claude to synthesize information from multiple sources
- **Markdown Reports**: Generates well-structured reports with citations
- **Configurable Depth**: Quick, standard, or deep research modes
- **CLI Interface**: Easy-to-use command-line tool

## Installation

### Prerequisites

- Python 3.10 or higher
- An Anthropic API key ([get one here](https://console.anthropic.com/))

### Install from source

```bash
# Clone the repository
git clone https://github.com/SDGuitarist/Alex-Guillen-Music.git
cd Alex-Guillen-Music

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Command Line

```bash
# Basic research
research-agent "artificial intelligence trends"

# Research with specific focus areas
research-agent "climate change" --focus "renewable energy,carbon capture,policy"

# Deep research with more sources
research-agent "quantum computing applications" --depth deep --max-sources 20

# Quick research
research-agent "Python 3.12 new features" --depth quick

# Specify output directory
research-agent "machine learning" --output ./my-reports

# Print to console only (don't save file)
research-agent "web development trends" --no-save
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--focus` | `-f` | Comma-separated focus areas |
| `--depth` | `-d` | Research depth: `quick`, `standard`, `deep` |
| `--max-sources` | `-m` | Maximum sources to gather (default: 10) |
| `--output` | `-o` | Output directory for reports |
| `--no-save` | | Don't save report to file |
| `--model` | | Claude model to use |
| `--env-file` | | Path to .env file |

### Python API

```python
import asyncio
from research_agent import ResearchAgent, ResearchQuery

async def main():
    # Initialize the agent
    agent = ResearchAgent()

    # Define your research query
    query = ResearchQuery(
        topic="The future of renewable energy",
        focus_areas=["solar power", "wind energy", "energy storage"],
        depth="standard",
        max_sources=10
    )

    # Run the research
    report = await agent.research(query)

    # Save the report
    filepath = agent.save_report(report)
    print(f"Report saved to: {filepath}")

    # Or get markdown directly
    print(report.to_markdown())

asyncio.run(main())
```

## Research Depths

| Depth | Search Queries | Pages Fetched | Best For |
|-------|---------------|---------------|----------|
| `quick` | 3 | 3 | Fast overviews |
| `standard` | 5 | 6 | Balanced research |
| `deep` | 8 | 10 | Comprehensive analysis |

## Output

Reports are saved as markdown files in the `reports/` directory (configurable). Each report includes:

- Title and generation timestamp
- Executive summary
- Multiple sections covering different aspects
- Full source list with URLs

## Project Structure

```
research-agent/
├── pyproject.toml          # Project configuration
├── .env.example            # Example environment variables
├── README.md               # This file
├── reports/                # Generated reports (created automatically)
└── src/
    └── research_agent/
        ├── __init__.py     # Package exports
        ├── agent.py        # Core research agent
        ├── cli.py          # Command-line interface
        ├── models.py       # Data models
        └── search.py       # Web search functionality
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run linting
ruff check src/

# Run tests
pytest
```

## License

MIT License

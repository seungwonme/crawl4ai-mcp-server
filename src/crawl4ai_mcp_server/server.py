"""MCP Server for Crawl4AI - Web document crawling tools.

Run with:
    uv run mcp_server.py
    or
    uv run mcp run mcp_server.py
"""

import sys
from pathlib import Path

from .core import crawl_documentation, crawl_single_page
from .configs.browser import FAST_CONFIG, STEALTH_CONFIG
from mcp.server.fastmcp import FastMCP

# Redirect print to stderr (STDIO transport uses stdout for JSON-RPC)
_original_print = print


def _stderr_print(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    _original_print(*args, **kwargs)


# Apply globally
import builtins

builtins.print = _stderr_print


def _get_browser_config(stealth: bool):
    """stealth 옵션에 따라 BrowserConfig 반환"""
    return STEALTH_CONFIG if stealth else FAST_CONFIG


# Create MCP server instance
mcp = FastMCP(
    name="crawl4ai-mcp-server",
    instructions="""Crawl4AI MCP Server - Web document crawling tools.

Available tools:
- crawl_page: Crawl a single page and return markdown content
- crawl_docs: Recursively crawl documentation sites (Deep Crawl)

Use crawl_page for single page content extraction.
Use crawl_docs for crawling entire documentation sites with link following.

Options:
- stealth: Enable stealth mode (playwright-stealth) for sites with bot detection
- strategy: Choose crawl strategy - "bfs" (breadth-first, default) or "dfs" (depth-first)""",
)


@mcp.tool()
async def crawl_page(
    url: str,
    output_dir: str | None = None,
    stealth: bool = False,
) -> str:
    """Crawl a single web page and return cleaned markdown content.

    Args:
        url: The URL to crawl
        output_dir: Optional directory to save the markdown file.
                   If not provided, returns markdown without saving.
        stealth: Enable stealth mode to bypass bot detection.
                Uses playwright-stealth with random user-agent.
                Slower but needed for sites that block automated crawlers.

    Returns:
        Cleaned markdown content of the page
    """
    browser_config = _get_browser_config(stealth)
    markdown = await crawl_single_page(url, output_dir, browser_config=browser_config)
    if not markdown:
        return f"Failed to crawl: {url}"
    return markdown


@mcp.tool()
async def crawl_docs(
    url: str,
    output_dir: str | None = None,
    max_pages: int = 100,
    max_depth: int = 2,
    url_prefix: str | None = None,
    strategy: str = "bfs",
    stealth: bool = False,
) -> str:
    """Recursively crawl a documentation site (Deep Crawl).

    Follows links within the same domain and saves each page as a markdown file.

    Args:
        url: The starting URL to crawl
        output_dir: Directory to save markdown files.
                   Defaults to domain name (e.g., docs_example_com)
        max_pages: Maximum number of pages to crawl (default: 100)
        max_depth: Maximum crawl depth from start URL (default: 2)
        url_prefix: Optional URL prefix filter.
                   Only crawls URLs starting with this prefix.
                   Example: "https://docs.example.com/api" to only crawl /api section
        strategy: Crawl strategy - "bfs" (breadth-first, default) or "dfs" (depth-first).
                 BFS explores all links at one depth before going deeper.
                 DFS explores as deep as possible before backtracking.
        stealth: Enable stealth mode to bypass bot detection.
                Uses playwright-stealth with random user-agent.

    Returns:
        Summary of crawled pages with URLs and file paths
    """
    if strategy not in ("bfs", "dfs"):
        return f"Invalid strategy: {strategy}. Use 'bfs' or 'dfs'."

    browser_config = _get_browser_config(stealth)
    results = await crawl_documentation(
        start_url=url,
        output_dir=output_dir,
        max_pages=max_pages,
        max_depth=max_depth,
        url_prefix=url_prefix,
        strategy=strategy,
        browser_config=browser_config,
    )

    if not results:
        return f"No pages crawled from: {url}"

    # Format results as summary
    summary_lines = [f"Crawled {len(results)} pages:\n"]
    for r in results:
        summary_lines.append(f"- [{r['depth']}] {r['url']} -> {r['file']}")

    # Add output directory info
    if results:
        output_path = Path(results[0]["file"]).parent
        while output_path.parent != output_path and output_path.name != output_dir:
            if output_path.parent.name == "":
                break
            output_path = output_path.parent
        summary_lines.append(f"\nSaved to: {output_path}/")

    return "\n".join(summary_lines)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

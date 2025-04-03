from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP

from config.browser import setup_browser_config
from config.markdown import setup_markdown_generator
from config.run import setup_run_config

mcp = FastMCP("Crawl4AI MCP Server")


@mcp.tool()
async def crawl_url(url: str) -> str:
    """Crawl a url and return the content

    Args:
        url: The url to crawl

    Returns:
        The content of the url in markdown format
    """
    # 설정 초기화
    md_generator = setup_markdown_generator()
    browser_config = setup_browser_config()
    run_config = setup_run_config(md_generator)

    # 크롤러 실행
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if isinstance(result, dict) and "markdown" in result:
                return str(result["markdown"])
            elif isinstance(result, dict) and "content" in result:
                return str(result["content"])
            return ""
    except Exception as e:
        print(f"Error during crawling: {e}")
        return ""


@mcp.tool()
async def crawl(url: str, depth: int = 1, max_pages: int = 10):
    """Starts crawling from the given URL, following links up to a specified depth

    Args:
        url: The url to crawl
        depth: The depth of the crawl
        max_pages: The maximum number of pages to crawl

    Returns:
        A list of crawled content in markdown format
    """
    # 설정 초기화
    md_generator = setup_markdown_generator()
    browser_config = setup_browser_config()
    run_config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=depth, include_external=False, max_pages=max_pages
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        markdown_generator=md_generator,
    )

    # 크롤러 실행
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            results = await crawler.arun(url, config=run_config)

            print(f"Crawled {len(results)} pages in total")

            # Access individual results
            for result in results[:3]:  # Show first 3 results
                print(f"URL: {result.url}")
                print(f"Depth: {result.metadata.get('depth', 0)}")
    except Exception as e:
        print(f"Error during crawling: {e}")
        return []


@mcp.tool()
async def ddg_search(query: str, max_result: int = 5):
    """Search the web using DuckDuckGo

    Args:
        query: The query to search for
        max_result: The maximum number of results to return

    Returns:
        The results of the search
    """
    results = DDGS().text(query, max_results=max_result)
    return list(results)


if __name__ == "__main__":
    mcp.run(transport="stdio")

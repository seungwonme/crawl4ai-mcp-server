"""Core crawler module (refactored)."""

import asyncio
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

from .configs.deep_crawl import create_bfs_strategy, create_dfs_strategy
from .strategies.content import clean_navigation_content
from .utils.domain import extract_domain, extract_output_dir_name
from .utils.path import url_to_filepath

# 기본 BrowserConfig: 빠른 텍스트 크롤링에 최적화
DEFAULT_BROWSER_CONFIG = BrowserConfig(
    headless=True,
    text_mode=True,
    light_mode=True,
    verbose=False,
)


async def crawl_single_page(
    url: str,
    output_dir: str = None,
    crawler_config: CrawlerRunConfig = None,
    browser_config: BrowserConfig = None,
) -> str:
    """단일 페이지 크롤링하여 마크다운 반환

    Args:
        url: 크롤링할 URL
        output_dir: 출력 디렉토리 (None이면 파일 저장 안 함)
        crawler_config: 크롤러 실행 설정 (None이면 기본 설정 사용)
        browser_config: 브라우저 설정 (None이면 기본 설정 사용)

    Returns:
        정리된 마크다운 텍스트
    """
    if crawler_config is None:
        from .configs.crawler import DOCS_CRAWL_CONFIG

        crawler_config = DOCS_CRAWL_CONFIG

    if browser_config is None:
        browser_config = DEFAULT_BROWSER_CONFIG

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url, config=crawler_config)

        if not result.success:
            print(f"❌ Failed: {url}")
            return ""

        # 마크다운 정리
        markdown_content = result.markdown.raw_markdown if result.markdown else ""
        cleaned_markdown = clean_navigation_content(markdown_content)

        # 파일 저장 (output_dir이 지정된 경우)
        if output_dir:
            domain = extract_domain(url)
            output_dir = output_dir or extract_output_dir_name(domain)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            file_path = url_to_filepath(url, output_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {url}\n\n")
                f.write(cleaned_markdown)

            print(f"✅ Saved to {file_path}")

        return cleaned_markdown


async def crawl_documentation(
    start_url: str,
    output_dir: str = None,
    max_pages: int = 100,
    max_depth: int = 2,
    url_prefix: str = None,
    strategy: str = "bfs",
    crawler_config: CrawlerRunConfig = None,
    browser_config: BrowserConfig = None,
) -> list[dict]:
    """공식문서 크롤링

    Args:
        start_url: 크롤링 시작 URL
        output_dir: 출력 디렉토리 (None이면 도메인명 사용)
        max_pages: 최대 크롤링 페이지 수
        max_depth: 최대 크롤링 깊이
        url_prefix: URL 프리픽스 필터 (지정 시 해당 프리픽스로 시작하는 URL만 크롤링)
        strategy: 크롤링 전략 ("bfs" 또는 "dfs")
        crawler_config: 크롤러 실행 설정 (None이면 기본 설정 사용)
        browser_config: 브라우저 설정 (None이면 기본 설정 사용)

    Returns:
        크롤링 결과 리스트
    """
    # 도메인 추출
    domain = extract_domain(start_url)

    # 출력 디렉토리 설정
    if output_dir is None:
        output_dir = extract_output_dir_name(domain)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Deep Crawl 전략 생성
    strategy_factory = create_dfs_strategy if strategy == "dfs" else create_bfs_strategy
    deep_crawl_strategy = strategy_factory(
        domain=domain,
        max_depth=max_depth,
        max_pages=max_pages,
        include_external=False,
        url_prefix=url_prefix,
    )

    # 크롤러 설정
    if crawler_config is None:
        from .configs.crawler import DOCS_CRAWL_CONFIG

        crawler_config = DOCS_CRAWL_CONFIG.clone(deep_crawl_strategy=deep_crawl_strategy)
    else:
        crawler_config = crawler_config.clone(deep_crawl_strategy=deep_crawl_strategy)

    if browser_config is None:
        browser_config = DEFAULT_BROWSER_CONFIG

    results = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        async for result in await crawler.arun(start_url, config=crawler_config):
            if result.success:
                depth = result.metadata.get("depth", 0)
                score = result.metadata.get("score", 0)

                # URL을 파일 경로로 변환
                file_path = url_to_filepath(result.url, output_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # 마크다운 정리
                markdown_content = result.markdown.raw_markdown if result.markdown else ""
                cleaned_markdown = clean_navigation_content(markdown_content)

                # 파일 저장
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {result.url}\n\n")
                    f.write(cleaned_markdown)

                print(f"✅ Depth {depth} | Score: {score:.2f} | {file_path}")
                results.append({"url": result.url, "depth": depth, "file": str(file_path)})
            else:
                print(f"❌ Failed: {result.url}")

    print(f"\n✅ Crawled {len(results)} pages")
    print(f"✅ Saved to {output_path}/")

    return results


if __name__ == "__main__":
    # 테스트
    asyncio.run(crawl_documentation("https://docs.crawl4ai.com", max_pages=10, max_depth=2))

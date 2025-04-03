import asyncio
import re

import pytest
import pytest_asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

from src.config.browser import setup_browser_config
from src.config.markdown import setup_markdown_generator
from src.config.run import setup_run_config
from tests.utils.file import save_png_to_unique_file, save_text_to_unique_file

stock_urls = [
    "https://finance.naver.com/sise/",
    "https://finance.yahoo.com/most-active",
]


# --- 세션 스코프 이벤트 루프 정의 (다시 추가) ---
# 세션 스코프의 비동기 픽스처(webcrawler)를 지원하기 위해 필요합니다.
# 전체 테스트가 진행되는 동안 계속 사용하겠다는 의미입니다. (테스트 시작할 때 만들고, 모든 테스트 끝날 때 정리)
# pylint: disable=unused-argument
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    # yield는 '잠시 빌려준다'는 의미입니다. 이 준비물 함수는 여기서 멈추고, 만들어진 loop (이벤트 루프 일꾼)를 필요한 곳(뒤에 나올 webcrawler 준비물)에 빌려줍니다. 그리고 모든 테스트가 끝날 때까지 기다립니다.
    yield loop
    loop.close()


# --- 세션 스코프 웹크롤러 픽스처 ---
# 정의된 세션 스코프 event_loop를 사용합니다.
# pylint: disable=unused-argument
@pytest_asyncio.fixture(scope="session")
async def webcrawler(event_loop):  # 세션 스코프 event_loop 파라미터 추가
    """테스트 세션 동안 AsyncWebCrawler 인스턴스를 관리합니다."""
    print("\n>>> [Session] 웹크롤러/브라우저 시작")
    browser_conf = setup_browser_config()
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        print(">>> [Session] 웹크롤러/브라우저 시작 완료")
        # 모든 테스트는 이 동일한 crawler 객체를 사용
        yield crawler
    print(">>> [Session] 웹크롤러/브라우저 종료 완료")


# --- 테스트 함수 (webcrawler 픽스처 사용) ---
@pytest.mark.asyncio  # 이 마크는 테스트 함수 자체의 실행 루프를 관리 (기본: 함수 스코프)
async def test_stock_data_crawling(webcrawler):  # 세션 스코프 webcrawler 주입
    """주식 데이터 크롤링 테스트"""
    print(f"\n>>> test_stock_data_crawling 실행 중 (크롤러 ID: {id(webcrawler)})")
    for url in stock_urls:
        md_generator = setup_markdown_generator()
        run_conf = setup_run_config(md_generator)
        result = await webcrawler.arun(url=url, run_config=run_conf)
        assert result is not None, f"{url} 크롤링 실패"
        assert result.markdown is not None, "마크다운 콘텐츠가 생성되지 않았습니다."
        file_name = url.rsplit("/", maxsplit=1)[-1]
        save_text_to_unique_file(result.markdown, f"stock_data_{file_name}", "md", "test_results")
        if result.screenshot:
            save_png_to_unique_file(
                result.screenshot, f"stock_screenshot_{file_name}", "test_results"
            )


@pytest.mark.asyncio  # 이 마크는 테스트 함수 자체의 실행 루프를 관리 (기본: 함수 스코프)
async def test_stock_price_format(webcrawler):  # 세션 스코프 webcrawler 주입
    """주식 가격 형식 테스트"""
    print(f"\n>>> test_stock_price_format 실행 중 (크롤러 ID: {id(webcrawler)})")
    url = "https://finance.naver.com/item/main.naver?code=005930"
    md_generator = setup_markdown_generator()
    run_conf = setup_run_config(md_generator)
    result = await webcrawler.arun(url=url, run_config=run_conf)
    assert result is not None, "주식 가격 크롤링 실패"
    assert result.markdown is not None, "마크다운 콘텐츠가 생성되지 않았습니다."
    price_pattern = r"[\d,]+"
    assert re.search(
        price_pattern, result.markdown
    ), "콘텐츠에서 유효한 가격 형식을 찾을 수 없습니다."


@pytest.mark.asyncio
async def test_deep_crawl(webcrawler):
    """깊은 크롤링 테스트"""
    print(f"\n>>> test_deep_crawl 실행 중 (크롤러 ID: {id(webcrawler)})")
    md_generator = setup_markdown_generator()
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=1, include_external=False),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        markdown_generator=md_generator,
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://docs.crawl4ai.com/", config=config)

        print(f"Crawled {len(results)} pages in total")

        # Access individual results
        for result in results[:3]:  # Show first 3 results
            print(f"URL: {result.url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")
            save_text_to_unique_file(result.markdown, "crawl", "md", "test_results")


async def main():
    # Configure a 2-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=1, include_external=False),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://docs.crawl4ai.com/core/deep-crawling/", config=config)

        print(f"Crawled {len(results)} pages in total")

        # Access individual results
        for result in results[:3]:  # Show first 3 results
            print(f"URL: {result.url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")
            save_text_to_unique_file(result.markdown, result.url, "md", "test_results")


if __name__ == "__main__":
    asyncio.run(main())

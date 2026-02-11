"""Crawler run configuration presets."""

from crawl4ai import CrawlerRunConfig, CacheMode
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

# 문서 크롤링용 기본 설정
DOCS_CRAWL_CONFIG = CrawlerRunConfig(
    # LXML 기반 고속 HTML 파싱
    scraping_strategy=LXMLWebScrapingStrategy(),
    # 캐시 우회 (항상 최신 데이터)
    cache_mode=CacheMode.BYPASS,
    # 불필요한 태그 제거 (nav는 링크 추출을 위해 유지)
    excluded_tags=["script", "style"],
    # 외부 이미지 제외
    exclude_external_images=True,
    # 오버레이 요소 제거 (팝업, 모달 등)
    remove_overlay_elements=True,
    # 스트리밍 활성화
    stream=True,
    verbose=True,
)

# 빠른 텍스트 추출용
TEXT_ONLY_CONFIG = CrawlerRunConfig(
    scraping_strategy=LXMLWebScrapingStrategy(),
    # 캐시 활성화
    cache_mode=CacheMode.ENABLED,
    # 외부 링크 제외
    exclude_external_links=True,
    # 최소 단어 수
    word_count_threshold=50,
    # 텍스트만 추출
    excluded_tags=["script", "style", "nav", "header", "footer", "aside"],
    verbose=False,
)

# 전체 데이터 수집용
COMPREHENSIVE_CONFIG = CrawlerRunConfig(
    scraping_strategy=LXMLWebScrapingStrategy(),
    # iframe 처리
    process_iframes=True,
    # 전체 페이지 스캔
    scan_full_page=True,
    # 스크린샷 캡처
    screenshot=True,
    # 캐시 우회
    cache_mode=CacheMode.BYPASS,
    verbose=True,
)


def create_custom_config(
    cache_enabled: bool = False,
    exclude_nav: bool = True,
    screenshot: bool = False,
    **kwargs,
) -> CrawlerRunConfig:
    """커스텀 크롤러 설정 생성

    Args:
        cache_enabled: 캐시 사용 여부
        exclude_nav: 네비게이션 제외 여부
        screenshot: 스크린샷 캡처 여부
        **kwargs: 추가 CrawlerRunConfig 파라미터
    """
    config = {
        "cache_mode": CacheMode.ENABLED if cache_enabled else CacheMode.BYPASS,
        "screenshot": screenshot,
        "exclude_external_images": True,
        "remove_overlay_elements": True,
        "stream": True,
        "verbose": True,
    }

    # 네비게이션 제외 설정
    if exclude_nav:
        config["excluded_tags"] = ["script", "style", "nav", "header", "footer"]
    else:
        config["excluded_tags"] = ["script", "style"]

    # 추가 파라미터 병합
    config.update(kwargs)

    return CrawlerRunConfig(**config)

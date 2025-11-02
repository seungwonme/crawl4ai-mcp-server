"""Deep crawling strategy configurations."""

from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import DomainFilter, FilterChain, URLPatternFilter
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer


def create_bfs_strategy(
    domain: str,
    max_depth: int = 2,
    max_pages: int = 100,
    include_external: bool = False,
    url_prefix: str = None,
) -> BFSDeepCrawlStrategy:
    """BFS(너비 우선 탐색) 전략 생성

    Args:
        domain: 허용할 도메인
        max_depth: 최대 크롤링 깊이
        max_pages: 최대 크롤링 페이지 수
        include_external: 외부 링크 포함 여부
        url_prefix: URL 프리픽스 필터 (지정 시 해당 프리픽스로 시작하는 URL만 크롤링)
    """
    filters = [DomainFilter(allowed_domains=[domain])]

    if url_prefix:
        filters.append(URLPatternFilter(patterns=[f"{url_prefix}*"], use_glob=True))

    filter_chain = FilterChain(filters)

    return BFSDeepCrawlStrategy(
        max_depth=max_depth,
        include_external=include_external,
        filter_chain=filter_chain,
        max_pages=max_pages,
    )


def create_best_first_strategy(
    domain: str,
    keywords: list[str],
    max_depth: int = 3,
    max_pages: int = 100,
    keyword_weight: float = 0.8,
) -> BestFirstCrawlingStrategy:
    """Best-First 전략 생성 (키워드 기반 우선순위)

    Args:
        domain: 허용할 도메인
        keywords: 우선순위 결정 키워드 리스트
        max_depth: 최대 크롤링 깊이
        max_pages: 최대 크롤링 페이지 수
        keyword_weight: 키워드 가중치
    """
    filter_chain = FilterChain([DomainFilter(allowed_domains=[domain])])

    scorer = KeywordRelevanceScorer(keywords=keywords, weight=keyword_weight)

    return BestFirstCrawlingStrategy(
        max_depth=max_depth,
        include_external=False,
        filter_chain=filter_chain,
        url_scorer=scorer,
        max_pages=max_pages,
    )


# 프리셋: 문서 사이트 크롤링용
def create_docs_strategy(domain: str, max_pages: int = 100) -> BestFirstCrawlingStrategy:
    """문서 사이트 크롤링 전략

    API 문서, 튜토리얼 등을 우선적으로 크롤링
    """
    keywords = ["guide", "tutorial", "documentation", "api", "reference", "docs", "example"]

    return create_best_first_strategy(
        domain=domain, keywords=keywords, max_depth=3, max_pages=max_pages, keyword_weight=0.9
    )

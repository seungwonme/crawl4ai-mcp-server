"""Domain processing utilities."""

from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    """URL에서 도메인 추출

    Args:
        url: 전체 URL

    Returns:
        도메인 (예: docs.crawl4ai.com)
    """
    parsed = urlparse(url)
    return parsed.netloc


def extract_output_dir_name(domain: str) -> str:
    """도메인에서 출력 디렉토리 이름 추출

    developers.figma.com -> developers_figma_com
    docs.crawl4ai.com -> docs_crawl4ai_com
    www.example.com -> example_com

    Args:
        domain: 도메인명

    Returns:
        출력 디렉토리 이름
    """
    # www. 제거
    domain = domain.replace("www.", "")

    # 모든 .을 _로 변경
    return domain.replace(".", "_")
